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
import importlib
import Work.globalvar as gv
from Work.log import Logger
logger = Logger('Function', 'DEBUG')


class Function:
    def __init__(self, entry, dis_mode, way_to_use='', help_info='', collect=None):
        """
        :param entry: entry of function.
        :param dis_mode: way to distribute the function(0 for allin, 1 for collective, 2 for local).
        :param way_to_use: format of order (like: 'SYSTEM;server;order' for system function)
        :param help_info: introduction of this function.
        :param collect: function to collect receives(default as below 'collective')
        """
        self.entry = entry
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
        :param message:Will be the order without the server part
        :param server_list:list of fileno
        :return:
        """
        results = ''
        for fileno in server_list:
            try:
                results += '-----------------------------------\n'
                if fileno == -1:
                    results += 'local(-1):  {}\n'.format(self.entry(gv.order_handler(message)[1:]))
                else:
                    conn = gv.connections[fileno]
                    conn.save_send(message)
                    results += '{}:  {}\n'.format(fileno, conn.save_receive())
            except Exception as e:
                results += '{}:Error!  {}\n'.format(fileno, e)
        return results


function_list = {}


def function_act(order):
    if order[0] not in function_list.keys():
        response = "No such function\n"
    else:
        response = function_list[order[0]](order[1:])
    return response

"""
def function_broadcast(order):
    if order[0] not in function_list:
        response = "No such function\n" \
                   "Do you need 'HELP'?"
    elif function_list[order[0]].argu_num != -1 and function_list[order[0]].argu_num + (
            2 if function_list[order[0]].dis_mode == 1 else 1) != len(order):
        # 1 for function name itself and another one for appointing.
        response = "Wrong number of arguments."
    else:
        response =
"""


if __name__ == '__main__':
    pass
else:
    temp_list = os.listdir(os.path.join(os.getcwd(), 'Function'))
    file_list = []
    for m_file in temp_list:
        x = m_file.rfind('.')
        if x != -1 and m_file[x:] == '.py':
            file_list.append(m_file[:-3])
    file_list.remove('__init__')
    file_list = map(lambda x: 'Function.{}'.format(x), file_list)

    for m_file in file_list:
        try:
            if m_file in sys.modules:
                cwm = reload(sys.modules[m_file])
            else:
                cwm = importlib.import_module(m_file)
            for (func, rf) in cwm.functions.items():
                func = func.upper()
                if 'entry' not in rf or 'argu_num' not in rf or 'dis_mode' not in rf:
                    raise
                if 'way_to_use' not in rf:
                    rf['way_to_use'] = ''
                if 'help' not in rf:
                    rf['help'] = ''
                if 'collect' not in rf:
                    rf['collect'] = None
                function_list[func] = Function(rf['entry'], rf['dis_mode'],
                                               rf['way_to_use'], rf['help_info'], rf['collect'])
        except Exception:
            logger.error("Failed to import function.{}:".format(m_file))
            logger.error(logger.traceback())