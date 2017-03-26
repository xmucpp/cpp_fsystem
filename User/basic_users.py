# -*- coding: utf-8 -*-
# @Time  : 2017/3/26 10:29
# @Author: FSOL
# @File  : basic_users.py

import Work.globalvar as gv
import config as cf
from Work.log import Logger
logger = Logger('User', 'DEBUG')

Collective = lambda x: x
Allin = lambda x: x.insert(1, 'ALL')
Local = lambda x: x.insert(1, '-1')
operation = {0: Allin, 1: Collective, 2: Local}


def server_receive(message):
    if message.find(cf.ORDER) == -1:
        order = [message]
    else:
        order = message.split(cf.ORDER)
    if order[0] not in gv.function_list.keys():
        logger.error('what are you talking about:{}'.format(order[0]))
        return
    if len(order) != gv.function_list[order[0]].argu_num + 1:
        return "wrong arguments"
    return gv.function_list[order[0]].entry(order[1:])


def console_order(message):
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
    if message.find(cf.ORDER) == -1:
        order = [message]
    else:
        order = message.split(cf.ORDER)
    order[0] = order[0].upper()
    if order[0] not in gv.function_list:
        return "No such function\n" \
               "Do you need 'HELP'?"
    elif order[0] == 'HELP':
        return str(gv.function_list.keys())[1:-1]
    elif gv.function_list[order[0]].argu_num+(2 if gv.function_list[order[0]].dis_mode == 1 else 1) != len(order):
        # 1 for function name itself and another one for appointing.
        return "Wrong number of arguments."
    else:
        operation[gv.function_list[order[0]].dis_mode](order)
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
        message = ';'.join([str(e) for e in order[2:]])
        return gv.function_list[func].collect(message, server_list)


Users = {
    'server': {'entry':console_order, 'receive':server_receive, 'leave':},
}