# -*- coding: utf-8 -*-
# @Time  : 2017/3/26 10:29
# @Author: FSOL
# @File  : __init__.py.py

import config as cf
import Work.globalvar as gv
from Work.log import Logger
import os
import sys
logger = Logger('User', 'DEBUG')


def default_entry(self):
    pass


def default_receive(self, message):
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


def default_leave(self):
    pass

temp_list = os.listdir(os.path.join(os.getcwd(), 'User'))
file_list = []
for m_file in temp_list:
    x = m_file.rfind('.')
    if x != -1 and m_file[x:] == '.py':
        file_list.append(m_file)
file_list.remove('__init__.py')
file_list = map(lambda x: 'User.{}'.format(x), file_list)
for m_file in file_list:
    try:
        if m_file in sys.modules:
            cwm = reload(m_file)
        else:
            cwm = __import__(m_file)
        for (name, way) in cwm.Users.items():
            if 'entry' in way:
                gv.user_list[name]['entry'] = way['entry']
            else:
                gv.user_list[name]['entry'] = default_entry
            if 'receive' in way:
                gv.user_list[name]['receive'] = way['receive']
            else:
                gv.user_list[name]['receive'] = default_receive
            if 'leave' in way:
                gv.user_list[name]['leave'] = way['leave']
            else:
                gv.user_list[name]['leave'] = default_leave
    except Exception:
        logger.error("Failed to load user.{}:".format(m_file))
        logger.error(logger.traceback())
