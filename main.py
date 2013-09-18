#!/usr/bin/env python

# Copyright (c) 2013 Jon Anders Haugum
# MIT License (See file LICENSE for details)

import datetime # isoformat srptime format: '%Y-%m-%dT%H:%M:%S.%f'
import logging
import os

import tornado.ioloop
import tornado.httpclient
import tornado.web

from bbqdaemon.regulator import cyberqwifi
from bbqdaemon.storage import DataStorage

class CyberQWiFi(object):
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
                data = cyberqwifi.parser(response.body)
                self.data_storage.store(datetime.datetime.now(), data)
            except cyberqwifi.CyberQWiFiException as e:
                logging.warning("Failed to parse xml: {}\nException: {}".format(response.body, e))
        nextpoll = self.poll_time + datetime.timedelta(seconds=interval)
        tornado.ioloop.IOLoop.instance().add_timeout(nextpoll - datetime.datetime.now(), self.poll)


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

