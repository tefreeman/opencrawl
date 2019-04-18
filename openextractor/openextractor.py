import json
import gzip
import io
import threading
import queue
import requests
import lxml
from bs4 import BeautifulSoup, Tag
from typing import Dict, Union, List, Callable
from recipe import Recipe
from helpers import cache_request, if_errs_save_file, get_highest_match
from saverecipe import SaveRecipes
from collections import OrderedDict
from enum import IntEnum
import pymongo
import multiprocessing
import  time


class ParseStatus(IntEnum):
    SUCCESS = 0
    NO_DATA = 1
    INVALID_PAGE = 2
    PARSING_ERRORS = 3
    BAD_URL = 4


class OpenExtractor:
    common_crawl_indexes_url = 'https://index.commoncrawl.org/collinfo.json'

    def __init__(self, target_url: str, collection_name: str, bulk_trigger_amt: int, extract_func: Callable[[BeautifulSoup, Recipe], None],
                 check_func: Callable[[str], bool], url_check: Callable[[BeautifulSoup], bool], url_remove: Callable[[str], str]):
        self.extract_recipe_func: Callable[[any, any], None] = extract_func
        self.check_page_func: Callable[[any], bool] = check_func
        self.url_check_func: Callable[[BeautifulSoup], bool] = url_check
        self.url_remove_func: Callable[[str], str] = url_remove
        self.matching_url_queue: queue.Queue = queue.Queue()
        self.threads: List[threading.Thread] = []
        self.domain_urls: Dict = {}
        self.parsed_urls = {}
        self.load_url_map('recipes', collection_name)
        self.indexes: List[str] = self.get_open_crawl_index_list()
        self.record_list = self.find_urls_in_indexes(target_url, self.indexes)
        self.save_thread = SaveRecipes('recipes', collection_name, bulk_trigger_amt).start()
        self.max_retries = 6
        self.max_thread_fail = 3

        self.connection_stats = {'parse_count': 0.001, 'parse_time': 0.001}

    def load_url_map(self, db_name: str, collection_name: str):
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        db_list = client.list_database_names()

        if db_name not in db_list:
            raise Exception('The given db name does not exist')

        db = client[db_name]
        collection = db[collection_name]

        cursor = collection.find({})
        for doc in cursor:
            self.parsed_urls[doc['url']] = True

    def start_worker(self):
        tries = 0
        while True:
            try:
                url = self.matching_url_queue.get()
                if url is None:
                    break
                self.save_thread.append(self.findRecipe(url))
                self.matching_url_queue.task_done()
                tries = 0

            except Exception as err:
                self.matching_url_queue.task_done()
                tries += 1
                if tries == 3:
                    print('\nthread has failed ', tries, ' in a row terminating thread\n', err , "\n")
                    return

    def run_crawl(self, start=0, end=-1):
        if start < 0 or end > len(self.record_list) or start > len(self.record_list):
            raise Exception("start and end is not valid")
        for i in range(1):
            t = threading.Thread(target=self.start_worker)
            t.start()
            self.threads.append(t)

        if end == -1:
            end = len(self.record_list)

        self.save_thread.set_url_count(end-start)

        for i in range(start, end):
            self.matching_url_queue.put(self.record_list.popitem()[1])

        # block until all tasks are done
        self.matching_url_queue.join()

        for i in range(1):
            self.matching_url_queue.put(None)

        for t in self.threads:
            t.join()

    def get_open_crawl_index_list(self) -> list:
        data = cache_request(self.common_crawl_indexes_url)
        data_json: List = json.loads(data)
        return data_json[0:20]

    def find_urls_in_indexes(self, domain, index_list) -> dict:
        record_set: OrderedDict = OrderedDict()
        print("[*] Trying target domain: %s" % domain)
        for index in index_list:
            print("[*] Trying index %s" % index['cdx-api'])
            cc_url = index['cdx-api'] + '?'
            cc_url += "url=%s&output=json" % domain
            response = cache_request(cc_url)
            if response:
                records = response.splitlines()
                for record in records:
                    parsed = json.loads(record)
                    if self.url_check_func(parsed['url']):
                        cleaned_url = self.url_remove_func(parsed['url'])
                        if cleaned_url not in self.parsed_urls:
                            if cleaned_url in record_set:
                                record_set[cleaned_url].append(parsed)
                            else:
                                record_set[cleaned_url] = []
                                record_set[cleaned_url].append(parsed)
                print("[*] Added %d results." % len(records))
        print("[*] Found a total of %d urls to crawl" % len(record_set), end=" | ")
        print("Already parsed %d urls" % len(self.parsed_urls))
        return record_set


    # ---------------------------
    # Downloads full page
    # ---------------------------
    @staticmethod
    def download_page(record) -> Union[str, None]:
        offset, length = int(record['offset']), int(record['length'])
        offset_end = offset + length - 1

        if length < 10000:
            return None

        if 'status' in record:
            if int(record['status']) > 300:
                return None

        # We'll get the file via HTTPS so we don't need to worry about S3 credentials
        # Getting the file on S3 is equivalent however - you can request a Range
        prefix = 'https://commoncrawl.s3.amazonaws.com/'

        # We can then use the Range header to ask for just this set of bytes
        try:
            resp = requests.get(prefix + record['filename'], headers={'Range': 'bytes={}-{}'.format(offset, offset_end)})

        # The page is stored compressed (gzip) to save space
        # We can extract it using the GZIP library
            raw_data = io.BytesIO(resp.content)
            f = gzip.GzipFile(fileobj=raw_data)

            # What we have now is just the WARC response, formatted:
            data = f.read()

            response = ""
            # crude check for 301 errors and other data get errors
            try:
                warc, header, response = data.strip().split(b'\r\n\r\n', 2)
            except Exception as err:
                return None
            return response

        except:
            return None

    def findRecipe(self, urls: list) -> Union[Recipe]:
        retries = 0
        error_parsed = None
        recipe = Recipe(None)
        for url in urls:
            recipe.set_url(url['url'])
            if retries > self.max_retries:
                break

            html_data = self.download_page(url)

            if html_data is None:
                recipe.set_error_status(ParseStatus.BAD_URL)
                retries += 1
                continue


            is_valid: ParseStatus = self.extract_recipe(html_data, recipe)
            recipe.set_error_status(is_valid)

            self.connection_stats['parse_count'] += 1

            if is_valid == ParseStatus.SUCCESS:
                return recipe
            else:
                retries += 1
                if is_valid == ParseStatus.PARSING_ERRORS:
                    error_parsed = recipe

        if error_parsed is not None:
            return error_parsed
        else:
            return recipe

    def extract_recipe(self, html_content: str, recipe: Recipe) -> ParseStatus:

        parser = BeautifulSoup(html_content, "lxml")

        if parser is None:
            recipe.append_errs("parser is None")
            recipe.append_parser(html_content)
            return ParseStatus.NO_DATA

        parser_body = parser.body

        if not self.check_page_func(parser.body):
            recipe.append_errs("Not recipe")
            recipe.append_parser(html_content)
            return ParseStatus.INVALID_PAGE

        self.extract_recipe_func(parser_body, recipe)

        if len(recipe.get_errs()) > 0:
            return ParseStatus.PARSING_ERRORS

        return ParseStatus.SUCCESS
