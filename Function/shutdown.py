# -*- coding: utf-8 -*-
# @Time  : 2017/3/25 11:17
# @Author: FSOL
# @File  : shutdown.py

"""
Shutdown this program on some server.
"""
import Work.globalvar as gv


def shutdown(order):
    gv.order_to_close = True
    return "Server is shutting down."

functions = {
    'shutdown': {'entry': shutdown, 'argu_num': 0, 'dis_mode': 1,
                 'way_to_use': 'SHUTDOWN;server',
                 'help_info': 'Shut down appointed servers.',
                 'collect': None}
}
