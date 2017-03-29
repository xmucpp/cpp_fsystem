# -*- coding: utf-8 -*-
# @Time  : 2017/3/26 10:29
# @Author: FSOL
# @File  : __init__.py.py

"""
__init__.py
==========================
Will count all user and write it into globalvar.user_list.
"""
import config as cf
import Function
from Work.log import Logger
import os
import sys
import importlib
logger = Logger('User', 'DEBUG')


def default_entry(self):
    pass


def default_receive(self, message):
    if message.find(cf.ORDER) == -1:
        order = [message]
    else:
        order = message.split(cf.ORDER)
    if order[0] not in Function.function_list.keys():
        logger.error('what are you talking about:{}'.format(order[0]))
        return
    if Function.function_list[order[0]].argu_num !=-1 and len(order) != Function.function_list[order[0]].argu_num + 1:
        return "wrong arguments"
    return Function.function_list[order[0]].entry(order[1:])


def default_leave(self):
    pass

temp_list = os.listdir(os.path.join(os.getcwd(), 'User'))
file_list = []
for m_file in temp_list:
    x = m_file.rfind('.')
    if x != -1 and m_file[x:] == '.py':
        file_list.append(m_file[:-3])
file_list.remove('__init__')
file_list = map(lambda x: 'User.{}'.format(x), file_list)

user_list = {}

for m_file in file_list:
    try:
        if m_file in sys.modules:
            cwm = reload(sys.modules[m_file])
        else:
            cwm = importlib.import_module(m_file)
        for (name, way) in cwm.Users.items():
            if name not in user_list:
                user_list[name] = {}
            if 'entry' in way:
                user_list[name]['entry'] = way['entry']
            else:
                user_list[name]['entry'] = default_entry
            if 'receive' in way:
                user_list[name]['receive'] = way['receive']
            else:
                user_list[name]['receive'] = default_receive
            if 'leave' in way:
                user_list[name]['leave'] = way['leave']
            else:
                user_list[name]['leave'] = default_leave
    except Exception:
        logger.error("Failed to load user.{}:".format(m_file))
        logger.error(logger.traceback())
