# This is a parallel scanner to process all apk files in a folder.

from multiprocessing import Queue, Process, pool, Lock, current_process

import os


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
        # TODO process apks files
        print(file_name)


class ParaScanner(object):

    def __init__(self):
        self.file_queue = Queue()
        self.max_process = 10

    def set_max_process(self, n):
        self.max_process = n

    def find_apk_files(self, folder_path):
        for root, dirs, files in os.walk(folder_path):
            for f in files:
                file_name, extension = os.path.splitext(f)
                if extension == '.py':
                    self.file_queue.put(os.path.join(root, file_name))

    def process_files(self):
        processes = []
        for i in range(self.max_process):
            p = ApkProcessor(self.file_queue)
            self.file_queue.put(None)
            p.start()
            processes.append(p)

        for p in processes:
            p.join()

    def scan(self, folder='.'):
        self.find_apk_files(folder)
        self.process_files()

if __name__ == '__main__':
    scanner = ParaScanner()
    scanner.scan()

