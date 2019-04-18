import pymongo
import threading
import time
from pprint import pprint
from pymongo.errors import BulkWriteError
from sys import stdout
from typing import List

from recipe import Recipe


class SaveRecipes:

    # Constructor function
    def __init__(self, db_name: str, collection_name: str, trigger_amt: int):

        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        db_list = self.client.list_database_names()

        if db_name not in db_list:
            raise Exception('The given db name does not exist')

        self.update_count: int = 0
        self.error_count: float = 0
        self.recipe_buffer: List = list()
        self.event: threading.Event = threading.Event()
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        self.bulk_update_trigger_amt = trigger_amt
        self.stopped = False
        self.url_count = 0
        self.type_error_count = [0, 0, 0, 0, 0]
        self.event.set()

    def start(self):
        threading.Thread(target=self.update, args=()).start()
        return self

    def set_url_count(self, url_count):
        self.url_count = url_count + 1
        self.update_count += 1

    def update(self):
        while True:
            if len(self.recipe_buffer) > self.bulk_update_trigger_amt:
                try:
                    if self.update_count > 0:
                        print('\x1b[2K\r')
                    self.event.clear()
               #     print('PyMongo excuting Bulk Write')
                    self.collection.bulk_write(self.recipe_buffer, ordered=False)
                    self.recipe_buffer = list()
                    self.event.set()
                except BulkWriteError as bwe:
                    # TODO: Add validation
                    print('PyMongo BulkWriteError')
                    pprint(bwe.code)
                    self.recipe_buffer = list()
                    self.event.set()
                except:
                    # Failed to save product into db.
                    # TODO: Add err message
                    print("[-] Upload Error")
                    self.stopped = True
            #    time.sleep(1)
            if self.stopped:
                return
            if self.update_count > 0:
                stdout.write(" \r count: %d | progress: %f%% | err count %d | err rate: %f%% |"
                             " err: no_data: %d, invalid_page: %d, parsing_errors: %d, bad_urls: %d"
                             % (self.update_count, float(self.update_count) / float(self.url_count), self.error_count,
                                float(self.error_count) / float(self.update_count), self.type_error_count[1],
                                self.type_error_count[2], self.type_error_count[3], self.type_error_count[4]))
                stdout.flush()
            time.sleep(1)

    # SUCCESS = 0
    # NO_DATA = 1
    # INVALID_PAGE = 2
    # PARSING_ERRORS = 3
    # BAD_URL = 4
    def append(self, recipe: Recipe):
        self.event.wait()
        self.update_count += 1
        if recipe.error_status == 0 or recipe.error_status == 3:
            pass
        elif recipe.error_status == 4:
            self.update_count -= 1
            self.url_count -= 1
        else:
            self.error_count += 1

        self.type_error_count[recipe.error_status] += 1
        self.recipe_buffer.append(pymongo.InsertOne(recipe.to_json()))

    def alive(self):
        if len(self.recipe_buffer) < 1:
            return False
        else:
            return True

    def stop(self):
        self.stopped = True
