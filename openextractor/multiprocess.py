import multiprocessing

class MultiProcess:
    queue: multiprocessing.Queue = multiprocessing.Queue()

    def __init__(self):
        # do other stuff
        pass

    def start_worker(self, queue_):
        while True:
            url = queue_.get()
            if url is None:
                break
            #recipe = self.findRecipe(url)
            print(url)

    def run_crawl(self, threadCount):
        queue_ = multiprocessing.Queue()
        for i in range(threadCount):
            self.threads.append(multiprocessing.Process(target=self.start_worker, args=(self, queue_)))

        for key, prop in self.record_list.items():
            queue_.put(prop)

        # block until all tasks are done
        for t in self.threads:
            t.start()