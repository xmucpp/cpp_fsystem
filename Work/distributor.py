# -*- coding: utf-8 -*-
# @Author: FSOL
# @File  : distributor.py

import json

import Work.globalvar as gv
import config as cf
from Work.log import Logger

logger = Logger('Distributor', 'DEBUG')


# {fuction's name: [arguments number, distribution mode(0 for allin, 1 for normal, 2 for local)]}
functions = {}
import basic_functions as b_f
file_list = map(lambda x: 'Work.basic_functions.{}'.format(x), b_f.file_list)
import additional_functions as a_f
file_list.extend(map(lambda x: 'Work.additional_functions.{}'.format(x), a_f.file_list))
for m_file in file_list:
    try:
        cwm = __import__(m_file)
        for (func, real_func) in cwm.functions.items():
            functions[func] = real_func
    except Exception:
        logger.error("Failed to import {}:".format(m_file))
        logger.error(logger.traceback())


def reloading():
    pass

Collective = lambda x: x
Allin = lambda x: x.insert(1, 'ALL')
Local = lambda x: x.insert(1, '-1')
operation = {0: Allin, 1: Collective, 2: Local}


def server_order(message):
    if message.find(cf.ORDER) == -1:
        order = [message]
    else:
        order = message.split(cf.ORDER)
    if order[0] not in server_operation.keys():
        logger.error('what are you talking about:{}'.format(order[0]))
        return
    if len(order) != arguments_number[order[0]]:
        return "wrong arguments"
    return server_operation[order[0]](order)


def man(order):
    """
    Introduce a function.
    :param order:
    :return: the way to use the order and info.
    """
    if order[1] in functions:
        return '%-20s          %-40s' % (functions[order[1]].how_to_use, functions[order[1]].help_info)
    else:
        return 'No such function'


def console_order(message):
    """
    Transfer the message for further execution.
    Split the order message into arguments list.
    Check whether the order is correct,
        i.e whether the function exists, whether number of arguments matches.
    Unify the appointing part.
    Except help and man, if it has its collect function, use it, otherwise use the default collect function.
    :param message:
    :return:
    """
    if message.find(cf.ORDER) == -1:
        order = [message]
    else:
        order = message.split(cf.ORDER)
    order[0] = order[0].upper()
    if order[0] not in functions:
        return "No such function\n" \
               "Do you need 'HELP'?"
    elif order[0] == 'HELP':
        return str(functions.keys())[1:-1]
    elif order[0] == 'MAN':
        return man(order)
    elif functions[order[0]].argu_num+(2 if functions[order[0]].dis_mode == 1 else 1):
        # 1 for function name itself and another one for appointing.
        return "Wrong number of arguments."
    else:
        operation[functions[order[0]].dis_mode](order)
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
        if functions[func].collect:
            return functions[func].collect(message, server_list)
        else:
            return functions[func].collective(message, server_list)
