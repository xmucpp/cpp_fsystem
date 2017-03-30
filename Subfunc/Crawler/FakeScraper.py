# -*- coding: utf-8 -*-
# @Author: FSOL
# @File  : FakeScraper.py

import time


def parse(url):
    print 'worker:{}'.format(url)
    time.sleep(1)
    return 0

crawler = {
    'FAKE': parse
}
