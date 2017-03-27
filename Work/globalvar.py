# -*- coding: utf-8 -*-
# @Author: FSOL
# @File  : globalvar.py

import time
import os


connections = {}

order_to_close = False
order_to_update = False

# -------Path---------------
PATH = os.path.abspath(os.path.dirname(__file__))
# -------time
PRESENT_DAY = str(time.strftime('%Y-%m-%d', time.localtime(time.time())))
