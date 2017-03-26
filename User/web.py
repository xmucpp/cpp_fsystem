# -*- coding: utf-8 -*-
# @Time  : 2017/3/26 10:59
# @Author: FSOL
# @File  : web.py

import config as cf
import Work.globalvar as gv
from Work.log import Logger
logger = Logger('User', 'DEBUG')


def web_entry(self):
    if 'jsinfo' in gv.function_list:
        self.save_send(gv.function_list['jsinfo']())
    else:
        self.save_send("jsinfo hasn't been installed!")
    self.disconnect()


Users = {
    'web': {'entry': web_entry}
}
