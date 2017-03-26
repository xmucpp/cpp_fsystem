# -*- coding: utf-8 -*-
# @Time  : 2017/3/25 11:17
# @Author: FSOL
# @File  : shutdown.py

from Work.Classes import Function

functions = {
    'shutdown': Function(5, 1,
            'SHUTDOWN;server','Shutdown specified server')
}

def shutdown(order):
    if [i.state for i in gv.worker.values()].count('Running'):
        return "Please kill all running work before shut down the server!"
    gv.order_to_close = True
    return "Server is shutting down."