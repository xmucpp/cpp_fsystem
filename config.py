# -*- coding: utf-8 -*-
# @Time  : 2017/2/21 20:04
# @Author: FSOL
# @File  : config.py

import socket
import os
import time

# ------Socket timeout-----
timeout = 20
# ------Redis main server--
RedisServer = '123.207.93.47'
RedisPort = ''
RedisPass = ''
# ------Local ip-----------
HOST = ''
PORT = 9813
# ------link method--------
master = ('123.207.93.47', 9813)
# -------Constant----------
OUTTIME = 60
# -------Code--------------
CONNECTPASSWORD = 'eb5e7c27b9b470a5eb676aa21d38546b'
CONNECTCOMFIRM = 'COMFIRM'
CONSOLEPASSWORD = '94464dc84e47eb0ced31e13ef1bc016f'
WEBPASSWORD = '4974335816508181dd4d675c4aa28a42'
CONNECTSUCCESS = 'Connection established'
BACKUP = 'B-'
ORDER = ';'
IPPORT = '#'
# -------Path---------------
ROOTPATH = '/home/ubuntu'
PATH = os.path.abspath(os.path.dirname(__file__))
# -------time
PRESENT_DAY = str(time.strftime('%Y-%m-%d', time.localtime(time.time())))

