#!/usr/bin/env python

# Copyright (c) 2013 Jon Anders Haugum
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import datetime # isoformat srptime format: '%Y-%m-%dT%H:%M:%S.%f'
import logging
import os
import xml.etree.ElementTree

import tornado.ioloop
import tornado.httpclient
import tornado.web

class CyberQWiFi(object):
    status_codes = {
        0: "OK",
        1: "HIGH",
        2: "LOW",
        3: "DONE",
        4: "ERROR",
        5: "HOLD",
        6: "ALARM",
        7: "SHUTDOWN",
    }

    def __init__(self, host, data_storage, active_poll_interval=1, passive_poll_interval=10):
        self.host = host
        self.active_poll_interval = active_poll_interval
        self.passive_poll_interval = passive_poll_interval
        self.consecutive_errors = 0
        self.data_storage = data_storage
        tornado.ioloop.IOLoop.instance().add_callback(self.poll)

    def poll(self):
        self.poll_time = datetime.datetime.now()
        logging.debug("polling")
        http_client = tornado.httpclient.AsyncHTTPClient()
        http_client.fetch("http://" + self.host + "/status.xml", self.handle_request)

    def handle_request(self, response):
        interval = self.active_poll_interval
        if response.error:
            self.consecutive_errors += 1
            if self.consecutive_errors > 3:
                interval = self.passive_poll_interval
            logging.debug("Request failed: {}".format(response.error))
        else:
            self.consecutive_errors = 0
            print(response.headers)
            try:
                root = xml.etree.ElementTree.fromstring(response.body)
                data = dict((child.tag, child.text) for child in root)
                self.data_storage.store(datetime.datetime.now(), data)
            except xml.etree.ElementTree.ParseError as e:
                logging.warning("Failed to parse xml: {}\nException: {}".format(response.body, e))
            except:
                pass
        nextpoll = self.poll_time + datetime.timedelta(seconds=interval)
        tornado.ioloop.IOLoop.instance().add_timeout(nextpoll - datetime.datetime.now(), self.poll)


class DataStorage(object):
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

    def store(self, time, data):
        with open(os.path.join(self.data_dir, "raw.log"), "a") as fp:
            fp.write(str(time))
            fp.write(": ")
            fp.write(str(data))
            fp.write("\n")
        print(data)
        print("Pit temp: {}".format(round((int(data['COOK_TEMP']) - 320) * 5.0 / 9.0) / 10.0))
        print("Output percent: {}".format(data['OUTPUT_PERCENT']))


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

application = tornado.web.Application([
    (r"/", MainHandler),
])

if __name__ == "__main__":
    import tornado.options
    tornado.options.parse_command_line()
    application.listen(8888)
    data_storage = DataStorage()
    cqwifi = CyberQWiFi(host="10.0.0.8", data_storage=data_storage)
    tornado.ioloop.IOLoop.instance().start()

