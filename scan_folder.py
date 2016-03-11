#!/usr/bin/evn python
''' This class scans a folder and find all .apk files and stores the data in the database
'''

import depriv
import os

import Queue


class Scanner(Object):
    def __init__(self):
        self.db_conn = None

    def scan_folder(self, folder_name):
        file_queue = Queue()

        for root, dirs, files in os.walk(folder_name):
            print files





