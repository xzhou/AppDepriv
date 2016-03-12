# This is a parallel scanner to process all apk files in a folder.

from multiprocessing import Queue, Process, pool, Lock, current_process
from depriv_tools.apk_processor import ApkProcessor

import os


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

