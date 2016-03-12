
from multiprocessing import Process, Queue


class ApkProcessor(Process):
    def __init__(self, file_queue, result_queue=None):
        Process.__init__(self)
        self.file_queue = file_queue
        self.result_queue = result_queue

    def run(self):
        while True:
            next_file = self.file_queue.get()
            if next_file is None:
                print(' %s: exiting '% self.name)
                break
            self.process_apk(next_file)

    def process_apk(self, file_name):
        pass

