# -*- coding: utf-8 -*-
# @Time  : 2017/3/25 16:58
# @Author: FSOL
# @File  : Function_class.py

import globalvar as gv


class Function:
    def __init__(self, entry, argu_num, dis_mode, way_to_use='', help_info='', collect=None):
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
        Default way to collect receiving respond.
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
