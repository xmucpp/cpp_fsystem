# -*- coding: utf-8 -*-
# @Time  : 2017/3/26 10:29
# @Author: FSOL
# @File  : basic_users.py

import config as cf
import Function
import Work.globalvar as gv
from Work.log import Logger
logger = Logger('User', 'DEBUG')

import json
Collective = lambda x: x
Allin = lambda x: x.insert(1, 'ALL')
Local = lambda x: x.insert(1, '-1')
operation = {0: Allin, 1: Collective, 2: Local}


def console_receive(self, message):
    """
    Transfer the message for further execution.
    Split the order message into arguments list.
    Check whether the order is correct,
        i.e whether the function exists, whether number of arguments matches.
    Unify the appointing part.
    Except help, if it has its collect function, use it, otherwise use the default collect function.
    :param message:
    :return:
    """
    order = gv.order_handler(message)
    if order[0] == 'HELP':
        response = str(Function.function_list.keys())[1:-1]
    elif order[0] not in Function.function_list:
        response = "No such function\n" \
               "Do you need 'HELP'?"
    else:
        operation[Function.function_list[order[0]].dis_mode](order)
        try:
            if order[1].upper() != 'ALL':
                server_list = json.loads('[{}]'.format(order[1]))
            else:
                server_list = filter(lambda x: gv.connections[x].level == 'server', gv.connections.keys())
                server_list.append(-1)
        except Exception as e:
            return "----ERROR!!!----\n" \
                   "Target server list Error\n" \
                   "Use 'ALL'(no case insensitive) or 1,3,4(fileno of server)\n" \
                   "{}".format(e)
        func = order[0]
        order.pop(1)
        message = ';'.join([str(e) for e in order])
        response = Function.function_list[func].collect(message, server_list)
    return response


Users = {
    'server': {},
    'console': {'receive': console_receive},
    'Unidentified': {}
}