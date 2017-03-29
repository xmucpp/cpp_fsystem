# -*- coding: utf-8 -*-
# @Time  : 2017/3/26 10:17
# @Author: FSOL
# @File  : man.py

"""
Introduce a function.
"""
import Function


def man(order):
    order[0] = order[0].upper()
    if order[0] in Function.function_list:
        return '%-20s          %-40s' % (Function.function_list[order[0]].way_to_use, Function.function_list[order[0]].help_info)
    else:
        return 'No such function.'

functions = {
    'man': {'entry': man, 'argu_num': 1, 'dis_mode': 2,
            'way_to_use': 'MAN;function',
            'help_info': 'Look up for help of certain function.(if exists)',
            'collect': None}
}
