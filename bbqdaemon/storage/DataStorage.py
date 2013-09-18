# Copyright (c) 2013 Jon Anders Haugum
# MIT License (See file LICENSE for details)

import datetime # isoformat srptime format: '%Y-%m-%dT%H:%M:%S.%f'
import logging
import os

class DataStorage(object):
    class Session(object):
        def __init__(self, time, filename):
            self.time = time
            self.filename = filename

        def _read_file(self, filename):
            data = []
            with open(filename) as fp:
                for line in fp:
                    data.append(line)
            return data

    def __init__(self, data_dir="data", store_interval=60):
        self.data_dir = data_dir
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        self.store_interval = store_interval
        self.last_time = None
        self.current_store = []

    def store(self, time, data):
        if not self.last_time or (time - self.last_time >
                datetime.timedelta(seconds=self.store_interval)):
            self.last_time = time
            timedata = dict(datetime=str(time), data=data)
            self.current_store.append(timedata)
            with open(os.path.join(self.data_dir, "raw.log"), "a") as fp:
                fp.write(str(time))
                fp.write(": ")
                fp.write(str(data))
                fp.write("\n")
        print(data)
        if data['COOK_TEMP'].isdigit():
            print("Pit temp: {}".format(round((int(data['COOK_TEMP']) - 320) * 5.0 / 9.0) / 10.0))
        else:
            print("Pit temp: {}".format(data['COOK_TEMP']))
        print("Output percent: {}".format(data['OUTPUT_PERCENT']))

    def sessions(self):
        pass

    def retrieve(self, session=None):
        pass


