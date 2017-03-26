# -*- coding: utf-8 -*-
# @Time  : 2017/3/26 10:29
# @Author: FSOL
# @File  : __init__.py.py

import config as cf
import Work.globalvar as gv
from Work.log import Logger
logger = Logger('User', 'DEBUG')


def default_entry():
    pass


def default_receive(message):
    if message.find(cf.ORDER) == -1:
        order = [message]
    else:
        order = message.split(cf.ORDER)
    if order[0] not in gv.function_list.keys():
        logger.error('what are you talking about:{}'.format(order[0]))
        return
    if len(order) != gv.function_list[order[0]].argu_num + 1:
        return "wrong arguments"
    return gv.function_list[order[0]].entry(order[1:])


def default_leave():
    pass
