# Copyright (c) 2013 Jon Anders Haugum
# MIT License (See file LICENSE for details)

import logging
import os
import xml.etree.ElementTree

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

class CyberQWiFiException(Exception):
    pass


def parser(body):
    """ Parses the data from CyberQ WiFi and gives and dict of values """
    try:
        root = xml.etree.ElementTree.fromstring(body)
    except xml.etree.ElementTree.ParseError as e:
        logging.warning("Failed to parse xml: {}\nException: {}".format(body, e))
        raise CyberQWifiException("Failed to parse xml")
    data = dict((child.tag, child.text) for child in root)
    for key, value in data.items():
        if key.endswith("_STATUS") and value.isdigit() \
                and int(value) <= max(status_codes.keys()):
            data[key] = status_codes[int(value)]
    return data

