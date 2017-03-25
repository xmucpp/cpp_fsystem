# __author__ = 'xjlin'
# -*- coding: utf-8 -*-

import datetime
import logging
import os
import time
from logging import handlers

from config import PATH

LOG_FOLDER = os.path.join(PATH, 'Log')
DATEFMT = '%Y-%m-%d %H:%M:%S'

MAPPING = {
    'CRITICAL': 50,
    'ERROR': 40,
    'WARNING': 30,
    'INFO': 20,
    'DEBUG': 10,
    'NOTSET': 0,
}


def makedir(abspath):

    if not os.path.exists(abspath):
        os.makedirs(abspath)
    return




if __name__ == "__main__":
    """Test code"""

    logger = Logger('crawler', 'INFO')
    for i in range(10):
        logger.info('error {}'.format(i))
        logger.warning('warning {}'.format(i))
    time.sleep(2)
    try:
        1/0
    except Exception, e:
        logger.traceback()
    logger.critical('your mother is die!!!!!!')




