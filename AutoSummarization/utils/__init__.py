#!/usr/bin/env python
# coding=utf-8
from __future__ import unicode_literals

import logging
import logging.handlers

from AutoSummarization import config


def getLogger(name):
    logger = logging.getLogger(name)
    watched_file_handler = logging.handlers.WatchedFileHandler(config['logging']['file'])
    watched_file_handler.setLevel(config['logging']['level'])
    watched_file_handler.setFormatter(logging.Formatter('%(name)s %(asctime)s %(levelname)8s %(message)s'))
    logger.addHandler(watched_file_handler)
    logger.setLevel(config['logging']['level'])
    return logger
