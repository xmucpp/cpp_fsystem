# -*- coding: utf-8 -*-
# @Time  : 2017/3/25 11:54
# @Author: FSOL
# @File  : Classes.py


class Function:
    def __init__(self, argu_num, dis_mode, help_info='', module=''):
        self.module = module
        self.help_info = help_info
        self.argu_num = argu_num
        self.dis_mode = dis_mode
