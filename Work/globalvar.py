# -*- coding: utf-8 -*-
# @Author: FSOL
# @File  : globalvar.py

import time
import os
import config as cf


connections = {}

order_to_close = False
order_to_update = False

# -------Path---------------
PATH = os.getcwd()
# -------time
PRESENT_DAY = str(time.strftime('%Y-%m-%d', time.localtime(time.time())))


def order_handler(message):
    if message.find(cf.ORDER) == -1:
        order = [message]
    else:
        order = message.split(cf.ORDER)
    order[0] = order[0].upper()
    return order

