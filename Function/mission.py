# -*- coding: utf-8 -*-
# @Time  : 2017/3/25 11:17
# @Author: FSOL
# @File  : mission.py

import time
import datetime
import threading
import Work.globalvar as gv
from Work.log import Logger
logger = Logger('Function', 'DEBUG')


class Mission:
    def __init__(self, state, hour, minute, event):
        self.state = state
        self.hour = int(hour)
        self.minute = int(minute)
        self.event = event

mission_list = {}


def deltatime(hour, min, sec=0):
    target_time = datetime.datetime(2017, 2, 18, hour, min, sec)
    current_time = datetime.datetime.now()
    return 86400 - ((current_time - target_time).seconds % 86400)


def waiter(order):
    try:
        timetowake = deltatime(int(order[1]), int(order[2]))
        while True:
            mission_list[order[3]].event.wait(timetowake)
            if mission_list[order[3]].event.isSet():
                break
            else:
                gv.function_list[order[3]].entry(order[4:])
                time.sleep(66)
                timetowake = deltatime(int(order[1]), int(order[2]))
        mission_list[order[3]].event.clear()
        mission_list[order[3]].state = 'Unsettled'
    except Exception:
        logger.traceback()
    return


def mission(order):
    if order[3] not in gv.function_list:
        return "No such function!"

    if order[0].upper() == 'SET':
        if order[3] in mission_list.keys() and mission_list[order[3]].state == 'Settled':
            return "Mission has already settled"
        else:
            mission_list[order[3]] = Mission('Settled', order[3], order[3], threading.Event())
            threading.Thread(target=waiter, args=[order]).start()
            return "Successfully settled"

    elif order[0].upper() == 'CANCEL':
        if order[3] not in mission_list.keys() or mission_list[order[3]].state == 'Unsettled':
            return "Mission isn't running"
        else:
            mission_list[order[3]].event.set()
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
