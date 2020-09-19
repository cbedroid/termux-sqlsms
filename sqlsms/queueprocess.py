import threading
from time import time
from functools import wraps
from queue import Queue
from time import sleep


class Threader():
    THREAD_TOTAL = 75
    def __init__(self,employer,jobs,extra=False):
        self.jobs = jobs # jobs to put in queue
        self.employer = employer # main function to perform jobs
        self.queue = Queue()
        self.extra = extra

        # for testing
        self.results = []
        self.process_ranned = []
        self.error = False

    def set_queue(self):
        # get all the data from self.jobs and place it into the queue
        for job in self.jobs:
            self.queue.put(job)

    @property
    def get_queue(self):
        if not self.queue.empty():
            return self.queue.get()
            

    def start_work(self):
        while True:
            work = self.get_queue
            if self.queue.empty() or work is None:
                break 

            working = self.employer(work,self.extra)
            self.results.append(working)
           
           # if there is no more work then break
           # just an extra precaution, queue.empty should handle this above
            try:
                self.queue.task_done()
            except:
                return 

    def threadit(self):
        for _ in range(self.THREAD_TOTAL):
            t = threading.Thread(target= self.start_work)
            t.daemon=True
            t.start()
            t.join()
            self.process_ranned.append(t)
            
    def run(self):
        self.set_queue()
        self.threadit()
        print('Done')
        return self.results
        
