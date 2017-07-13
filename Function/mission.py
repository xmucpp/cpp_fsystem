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
import json

import Work.globalvar as gv
import Function
from Work.log import Logger

logger = Logger('Function', 'DEBUG')


class Mission:
    ids = range(100, 0, -1)
    S_ON = 'Activated'
    S_OFF = 'Deactivated'

    def __init__(self, id=-1, hour=0, minute=0, message='', event=None, state=S_ON):
        if id == -1:
            if len(Mission.ids) != 0:
                self.id = Mission.ids.pop()
            else:
                raise ZeroDivisionError
        else:
            if id in Mission.ids:
                self.id = id
                Mission.ids.remove(id)
            else:
                raise ZeroDivisionError

        self.hour = int(hour)
        self.minute = int(minute)
        self.message = message
        self.event = event
        self.state = state

    def __deltatime(self, sec=0):
        target_time = datetime.datetime(2017, 2, 18, self.hour, self.minute, sec)
        current_time = datetime.datetime.now()
        return 86400 - ((current_time - target_time).seconds % 86400)

    def waiter(self):
        self.state = Mission.S_ON
        order = gv.order_handler(self.message)
        try:
            timetowake = self.__deltatime()
            while True:
                self.event.wait(timetowake)
                if self.event.isSet():
                    break
                else:
                    Function.function_act(order)
                    time.sleep(66)
                    timetowake = self.__deltatime()
        except Exception:
            logger.traceback()
        finally:
            self.event.clear()
            self.state = Mission.S_OFF
        return

    def worker(self):
        thread = threading.Thread(target=self.waiter, args=[])
        thread.setDaemon(True)
        thread.start()

mission_list = {}
SAVE_DIR = 'Data/mission.sav'


def writefile():
    with open(SAVE_DIR, 'w') as f:
        for mission in mission_list.values():
            f.write('{}\n'.format(json.dumps([mission.id, mission.hour, mission.minute, mission.message, mission.state])))


def readfile():
    with open(SAVE_DIR, 'r') as f:
        lines = f.readlines()
    for line in lines:
        js = json.loads(line[:-1])
        mission_list[js[0]] = Mission(id=js[0], hour=js[1], minute=js[2], message=js[3], event=threading.Event(), state=js[4])
        logger.debug(Mission.ids)
        logger.debug(js[0])
        try:
            Mission.ids.remove(js[0])
        except Exception:
            logger.traceback()
        if js[4] == Mission.S_ON:
            mission_list[js[0]].worker()


def mission(order):
    """
    NEW;hour;minute;message
    ON;mission id
    OFF;mission id
    :param order:order[0]:set/cancel order[1]:order[2] hour:minute order[3]:func order[4:]:arguments
    :return:
    """
    order[0] = order[0].upper()
    if order[0] == 'NEW':
        if order[3] not in Function.function_list:
            response = "No such function!"
        else:
            message = (';'.join([str(e) for e in order[3:]]))
            new_mission = Mission(hour=order[1], minute=order[2], event=threading.Event(), message=message)
            mission_list[new_mission.id] = new_mission
            new_mission.worker()
            response = "Successfully settled"
    elif order[0] == 'ON':
        if order[1] in mission_list:
            if mission_list[order[1]].state == Mission.S_OFF:
                mission_list[order[1]].worker()
            response = "Successfully ON"
        else:
            response = "No such mission!"
    elif order[0] == 'OFF':
        if order[1] in mission_list:
            if mission_list[order[1]].state == Mission.S_ON:
                mission_list[order[1]].event.set()
            response = "Successfully OFF"
        else:
            response = "No such mission!"
    else:
        response = "No such order!\n" \
                   "you can NEW, ON or OFF a mission."

    writefile()
    return response

functions = {
    'mission': {'entry': mission, 'argu_num': -1, 'dis_mode': 1,
                'way_to_use': 'MISSION;server;act;hour;min;func;func_argus',
                'help_info': 'act = SET/CANCEL and func = name of function, it will run every day at hour:min if set.',
                'collect': None}
}

if __name__ == "__main__":
    pass
else:
    readfile()

