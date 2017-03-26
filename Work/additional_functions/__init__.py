# -*- coding: utf-8 -*-
# @Time  : 2017/3/25 11:14
# @Author: FSOL
# @File  : __init__.py.py

import os
import sys

import Work.globalvar as gv
from Work.log import Logger
from Work.Function_class import Function
logger = Logger.logger('Process', 'DEBUG')

temp_list = os.listdir(os.path.join(os.getcwd(), 'Work', 'additional_functions'))
file_list = []
for m_file in temp_list:
    x = m_file.rfind('.')
    if x != -1 and m_file[x:] == '.py':
        file_list.append(m_file)
file_list.remove('__init__.py')
file_list = map(lambda x: 'Work.additional_functions.{}'.format(x), file_list)

for m_file in file_list:
    try:
        if m_file in sys.modules:
            cwm = reload(m_file)
        else:
            cwm = __import__(m_file)
        for (func, rf) in cwm.functions.items():
            if 'entry' not in rf or 'argu_num' not in rf or 'dis_mode' not in rf:
                raise
            if 'way_to_use' not in rf:
                rf['way_to_use'] = ''
            if 'help' not in rf:
                rf['help'] = ''
            if 'collect' not in rf:
                rf['collect'] = None
            gv.function_list[func] = Function(rf['entry'], rf['argu_num'], rf['dis_mode'],
                                              rf['way_to_use'], rf['help_info'], rf['collect'])
    except Exception:
        logger.error("Failed to import additional.{}:".format(m_file))
        logger.error(logger.traceback())
