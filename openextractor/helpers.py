from os import path, mkdir
from requests import get
from typing import List, TypeVar, Tuple
import pymongo


def delete_duplicates_by_key(collection: pymongo.collection, key_str: str) -> int:
    docs: dict = {}
    cursor = collection.find({})
    bulk_ops: List[str] = []
    for doc in cursor:
        if doc['url'] not in docs:
            docs[doc['url']] = []
        docs[doc['url']].append(doc)

    for key, val in docs.items():
        if len(val) > 1:
            for i in range(1, len(val)):
                bulk_ops.append(val[i]['_id'])
    if len(bulk_ops) > 0:
        collection.remove({'_id': {'$in': bulk_ops}})
    return len(bulk_ops)


def transformUrlToFileName(url: str):
    if url.find('https://') is not -1:
        url = url.replace('https://', 'https')
    if url.find('http://') is not -1:
        url = url.replace('http://', 'http')
    url = url.replace('.', '')
    url = url.replace('=', '')
    url = url.replace('/', '')
    url = url.replace('?', '')
    url = url.replace('*', '')
    url = url.replace('#', '')
    return url


def cache_request(url: str):
    file_dir = 'cache/'
    file_path = file_dir + transformUrlToFileName(url)
    if path.exists(file_path):
        with open(file_path, 'rb')as fr:
            return fr.read()
    else:
        response = get(url)
        if response.status_code == 200:
            with open(file_path, 'wb') as f:
                f.write(response.content)
                return response.content
        else:
            raise Exception('response code not 200 in cache_request')


def if_errs_save_file(url: str, content: str):
    file_dir = 'error/'
    if not path.exists(file_dir):
        mkdir(file_dir)
    file_path = file_dir + transformUrlToFileName(url)
    if not path.exists(file_path):
        write_mode = ''
        try:
            if isinstance(content, str):
                write_mode = "w"
            elif isinstance(content, (bytearray, bytes)):
                write_mode = "wb"
            else:
                raise Exception("unknown file data type")

            with open(file_path, write_mode) as f:
                    f.write(content)
        except:
            raise Exception("unable to save err file")
    return


T = TypeVar('T')


# comes with fast Logic to cancel loop early if determines first element has higher than half matches
# -1 match percent signifies that the list passed is of length 1 (cannot match with anything but itself)
def get_highest_match(items: List[T]) -> Tuple[T, float]:
    length = len(items)
    if length == 1:
        return items[0], -1
    counter_list: List[int] = []
    for m in range(length):
        counter_list.append(0)

    for i in range(length):
        for j in range(i + 1, length):
            if items[i] == items[j]:
                counter_list[i] += 1
                counter_list[j] += 1
        if counter_list[i] > length / 2:
            break
    index_val = max(counter_list)
    return items[counter_list.index(index_val)], index_val / (length - 1)

