# -*- coding: utf-8 -*-
# @Time  : 2017/3/25 11:17
# @Author: FSOL
# @File  : mission.py

"""
Set timed task.
"""

import time
import datetime
import threading
import Function
from Work.log import Logger
logger = Logger('Function', 'DEBUG')


class Mission:
    def __init__(self, hour, minute, event, order):
        self.hour = int(hour)
        self.minute = int(minute)
        self.event = event
        self.order = order

mission_list = {}


def deltatime(hour, min, sec=0):
    target_time = datetime.datetime(2017, 2, 18, hour, min, sec)
    current_time = datetime.datetime.now()
    return 86400 - ((current_time - target_time).seconds % 86400)


def waiter(order):
    message = (';'.join([str(e) for e in order[3:]])).upper()
    try:
        timetowake = deltatime(int(order[1]), int(order[2]))
        while True:
            mission_list[message].event.wait(timetowake)
            if mission_list[message].event.isSet():
                break
            else:
                Function.function_list[order[3]].entry(order[4:])
                time.sleep(66)
                timetowake = deltatime(int(order[1]), int(order[2]))
        mission_list[message].event.clear()
        mission_list.pop(message)
    except Exception:
        logger.traceback()
    return


def mission(order):
    """
    :param order:order[0]:set/cancel order[1]:order[2] hour:minute order[3]:func order[4:]:arguments
    :return:
    """
    if order[3] not in Function.function_list:
        return "No such function!"
    message = (';'.join([str(e) for e in order[3:]])).upper()
    if order[0].upper() == 'SET':
        if message in mission_list.keys():
            return "Mission has already settled"
        else:
            mission_list[message] = Mission(order[1], order[2], threading.Event(), message)
            threading.Thread(target=waiter, args=[order]).start()
            return "Successfully settled"

    elif order[0].upper() == 'CANCEL':
        if message not in mission_list.keys():
            return "Mission isn't running"
        else:
            mission_list[message].event.set()
            mission_list.pop(message)
            return "Successfully canceled"
    else:
        return "No such order!\n" \
               "you can either set or cancel a mission."

functions = {
    'mission': {'entry': mission, 'argu_num': -1, 'dis_mode': 1,
                'way_to_use': 'MISSION;server;act;hour;min;func;func_argus',
                'help_info': 'act = SET/CANCEL and func = name of function, it will run every day at hour:min if set.',
                'collect': None}
}
