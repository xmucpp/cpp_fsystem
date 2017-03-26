# -*- coding: utf-8 -*-
# @Time  : 2017/3/25 16:06
# @Author: FSOL
# @File  : system.py


def system(order):
    status, results = commands.getstatusoutput(order[1])
    if status == 0 and results != '':
        return results
    elif status == 0 and results == '':
        return "Success!\n"
    else:
        return 'ERROR:{}\n{}\n'.format(status, results)