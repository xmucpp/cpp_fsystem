# -*- coding: utf-8 -*-
# @Time  : 2017/3/25 11:14
# @Author: FSOL
# @File  : __init__.py.py

import os
temp_list = os.listdir(os.path.join(os.getcwd(), 'Work', 'additional_functions'))
file_list = []
for m_file in temp_list:
    x = m_file.rfind('.')
    if x != -1 and m_file[x:] == '.py':
        file_list.append(m_file)
file_list.remove('__init__.py')