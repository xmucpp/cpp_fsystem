# -*- coding: utf-8 -*-
# @Time  : 2017/3/27 22:15
# @Author: FSOL
# @File  : __init__.py.py

import os
import sys
import importlib
from Work.log import Logger

logger = Logger('Crawler', 'DEBUG')

temp_list = os.listdir(os.path.join(os.getcwd(), 'Subfunc', 'Crawler'))
file_list = []
for m_file in temp_list:
    x = m_file.rfind('.')
    if x != -1 and m_file[x:] == '.py':
        file_list.append(m_file[:-3])
file_list.remove('__init__')
file_list = map(lambda x: 'Subfunc.Crawler.{}'.format(x), file_list)

crawler_list = {}

for m_file in file_list:
    try:
        if m_file in sys.modules:
            cwm = reload(sys.modules[m_file])
        else:
            cwm = importlib.import_module(m_file)
        for (name, way) in cwm.crawler.items():
            crawler_list[name] = way
    except Exception:
        logger.error("Failed to load user.{}:".format(m_file))
        logger.error(logger.traceback())
