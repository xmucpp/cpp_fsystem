# -*- coding: utf-8 -*-
# @Time  : 2017/3/26 14:23
# @Author: FSOL
# @File  : __init__.py.py

"""
__init__.py
=======================
Will count all functions and write them into globalvar.function_list
"""
import os
import sys

import Work.globalvar as gv
from Work.log import Logger
logger = Logger('Process', 'DEBUG')


class Function:
    def __init__(self, entry, argu_num, dis_mode, way_to_use='', help_info='', collect=None):
        """
        :param entry: entry of function.
        :param argu_num: number of arguments.(Not include its name and appointing part)
        :param dis_mode: way to distribute the function(0 for allin, 1 for collective, 2 for local).
        :param way_to_use: format of order (like: 'SYSTEM;server;order' for system function)
        :param help_info: introduction of this function.
        :param collect: function to collect receives(default as below 'collective')
        """
        self.entry = entry
        self.argu_num = argu_num
        self.dis_mode = dis_mode
        self.way_to_use = way_to_use
        self.help_info = help_info
        if not collect:
            self.collect = self.collective
        else:
            self.collect = collect

    def collective(self, message, server_list):
        """
        Default way to send out and collect receiving respond.
        :param message:
        :param server_list:list of fileno
        :return:
        """
        results = ''
        for fileno in server_list:
            conn = gv.connections[fileno]
            try:
                results += '-----------------------------------\n'
                if fileno == -1:
                    results += 'local(-1):  {}\n'.format(self.entry(message))
                else:
                    conn.save_send(message)
                    results += '{}:  {}\n'.format(fileno, conn.recv(1024))
            except Exception as e:
                results += '{}:Error!  {}\n'.format(fileno, e)
        return results


temp_list = os.listdir(os.path.join(os.getcwd(), 'Work', 'basic_functions'))
file_list = []
for m_file in temp_list:
    x = m_file.rfind('.')
    if x != -1 and m_file[x:] == '.py':
        file_list.append(m_file)
file_list.remove('__init__.py')
file_list = map(lambda x: 'Work.basic_functions.{}'.format(x), file_list)

function_list = {}

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
            function_list[func] = Function(rf['entry'], rf['argu_num'], rf['dis_mode'],
                                              rf['way_to_use'], rf['help_info'], rf['collect'])
    except Exception:
        logger.error("Failed to import basic.{}:".format(m_file))
        logger.error(logger.traceback())
