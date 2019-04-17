import threading
import pymongo
from pymongo.errors import BulkWriteError
import time
from pprint import pprint
from recipe import Recipe
from sys import stdout
from typing import List


class SaveRecipes:

    # Constructor function
    def __init__(self, db_name: str, collection_name: str, trigger_amt: int, url_count: int):

        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        db_list = self.client.list_database_names()

        if db_name not in db_list:
            raise Exception('The given db name does not exist')

        self.update_count: int = 0
        self.recipe_buffer: List = list()
        self.event: threading.Event = threading.Event()
        self.lock: threading.Lock = threading.Lock()
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        self.bulk_update_trigger_amt = trigger_amt
        self.stopped = False
        self.url_count = url_count
        self.event.set()

    def start(self):
        threading.Thread(target=self.update, args=()).start()
        return self

    def update(self):
        while True:
            if len(self.recipe_buffer) > self.bulk_update_trigger_amt:
                try:
                    print('\x1b[2K\r')
                    self.event.clear()
                    print('PyMongo excuting Bulk Write')
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
            stdout.write(" \r count: %d | progress: %d%%" % (self.update_count, self.update_count / self.url_count))
            stdout.flush()
            time.sleep(1)

    def append(self, recipe: Recipe):
        self.event.wait()
        if recipe is not None:
            self.lock.acquire()
            self.update_count += 1
            self.recipe_buffer.append(pymongo.InsertOne(recipe.to_json()))
            self.lock.release()

    def alive(self):
        if len(self.recipe_buffer) < 1:
            return False
        else:
            return True

    def stop(self):
        self.stopped = True
