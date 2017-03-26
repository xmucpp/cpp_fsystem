# -*- coding: utf-8 -*-
# @Time  : 2017/3/26 10:17
# @Author: FSOL
# @File  : man.py

import Work.globalvar as gv


def man(order):
    """
    Introduce a function.
    :param order:
    :return: the way to use the order and info.
    """
    if order[1] in gv.function_list:
        return '%-20s          %-40s' % (gv.function_list[order[1]].how_to_use, gv.function_list[order[1]].help_info)
    else:
        return 'No such function.'