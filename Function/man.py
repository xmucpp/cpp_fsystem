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
    if order[0] in gv.function_list:
        return '%-20s          %-40s' % (gv.function_list[order[0]].how_to_use, gv.function_list[order[0]].help_info)
    else:
        return 'No such function.'

functions = {
    'man': {'entry': man, 'argu_num': 1, 'dis_mode': 2,
            'way_to_use': 'MAN;function',
            'help_info': 'Look up for help of certain function.(if exists)',
            'collect': None}
}