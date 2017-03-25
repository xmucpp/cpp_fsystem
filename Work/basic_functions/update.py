# -*- coding: utf-8 -*-
# @Time  : 2017/3/25 11:16
# @Author: FSOL
# @File  : update.py


def update(order):
    status, results = commands.getstatusoutput('git pull')
    if status == 0:
        gv.order_to_update = True
        return results
    else:
        return 'Update failed...\n{}  {}'.format(status, results)