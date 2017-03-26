# -*- coding: utf-8 -*-
# @Time  : 2017/3/25 11:16
# @Author: FSOL
# @File  : update.py
"""
Update files and reload.
"""

import commands

import Work.globalvar as gv


def update(order):
    status, results = commands.getstatusoutput('git pull')
    if status == 0:
        gv.order_to_update = True
        return results
    else:
        return 'Update failed...\n{}  {}'.format(status, results)

functions = {
    'update': {'entry': update, 'argu_num': 0, 'dis_mode': 1,
               'way_to_use': 'UPDATE;server',
               'help_info': 'Update files from git by "git pull" on every server and reload.',
               'collect': None}
}