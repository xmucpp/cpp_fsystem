# -*- coding: utf-8 -*-
# @Author: FSOL
# @File  : distributor.py

import json

import serverops as sv
import Work.globalvar as gv
import config as cf
from Work.log import Logger
from Work.Classes import Function

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
            functions[func].module = cwm
    except Exception:
        logger.error("Failed to import {}:".format(m_file))
        logger.error(logger.traceback())


def reloading():
    pass


# ------------------API
server_operation = {'SYSTEM': sv.system, 'CONNECT': sv.connect, 'INFO': sv.info, 'JSINFO': sv.jsinfo,
                    'STATISTICS': sv.statistics, 'CRAWLER': sv.crawler, 'MISSION': sv.mission,
                    'SHUTDOWN': sv.shutdown, 'UPDATE': sv.update, 'CANCEL': sv.cancel}
arguments_number = {'SYSTEM': 2, 'CONNECT': 4, 'INFO': 1, 'JSINFO': 1,
                    'STATISTICS': 1, 'CRAWLER': 2, 'MISSION': 5,
                    'SHUTDOWN': 1, 'UPDATE': 1, 'CANCEL': 2}
Collective = lambda x: x
Allin = lambda x: x.insert(1, 'ALL')
Local = lambda x: x.insert(1, '-1')

operation = {
    'SYSTEM': Collective,
    'CONNECT': Allin,
    'INFO': Collective,
    'STATISTICS': Allin,
    'CRAWLER': Collective,
    'SHUTDOWN': Collective,
    'UPDATE': Collective,
    'CANCEL': Collective,
    'MISSION': Collective,
    'JSINFO': Allin,
    'HELP': 0
}

help_list = '--------Caution: All servers are specified by its fileno\n'


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


def jsinfo(message, target_list):
    results = {'sl': len(gv.serverlist),
               'cl': len(gv.console),
               'ul': len(gv.unidentified),
               'wk': {cf.RedisServer: {work: {'s': gv.worker[work].state,
                     't': gv.worker[work].table} for work in gv.worker.keys()}},
               'st': {work: gv.crawlerstatis[work] for work in gv.worker.keys()},
               'ms': {mission: {'s': gv.mission_list[mission].state,
                     'h': gv.mission_list[mission].hour, 'm': gv.mission_list[mission].minute}
                      for mission in gv.mission_list.keys()},
               'Wsl': {}, 'Wms': {}
               }
    for target in target_list:
        try:
            if target == -1:
                pass
            else:
                gv.serverlist[target].send(message)
                temp = json.loads(gv.serverlist[target].recv(1024))
                if temp['sl'] != results['sl']:
                    results['Wsl'][gv.serverlist[target].getpeername()[0]] = temp['sl']
                results['cl'] += temp['cl']
                results['ul'] += temp['ul']
                results['wk'][gv.serverlist[target].getpeername()[0]] = {}
                for work in temp['wk']:
                    results['wk'][gv.serverlist[target].getpeername()[0]][work] = \
                        {'s': temp['wk'][work]['s'], 't': temp['wk'][work]['t']}
                    results['st'][work] += temp['wk'][work]['c']
                results['Wms'][gv.serverlist[target].getpeername()[0]] = {}
                for mission in temp['ms']:
                    if results['ms'][mission] != temp['ms'][mission]:
                        results['Wms'][gv.serverlist[target].getpeername()[0]][mission] = temp['ms'][mission]
        except Exception:
            logger.error(logger.traceback())
    return json.dumps(results)


def collective(order):
    try:
        if order[1].upper() != 'ALL':
            target_list = json.loads('[{}]'.format(order[1]))
        else:
            target_list = gv.serverlist.keys()
            target_list.append(-1)
    except Exception as e:
        return "----ERROR!!!----\n" \
               "Target server list Error\n" \
               "Use 'ALL'(no case insensitive) or 1,3,4(fileno of server)\n" \
               "{}".format(e)

    order.pop(1)
    message = ';'.join([str(e) for e in order])
    results = ''
    if order[0] == 'JSINFO':
        return jsinfo(message, target_list)
    for target in target_list:
        try:
            results += '-----------------------------------\n'
            if target == -1:
                results += 'local(-1):  {}\n'.format(server_order(message))
            else:
                gv.serverlist[target].send(message)
                results += '{}:  {}\n'.format(target, gv.serverlist[target].recv(1024))
        except Exception as e:
            results += '{}:Error!  {}\n'.format(target, e)

    return results


def console_order(message):
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
    else:
        operation[functions[order[0]].dis_mode](order)
        return collective(order)
