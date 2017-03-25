# -*- coding: utf-8 -*-
# @Time  : 2017/3/25 11:17
# @Author: FSOL
# @File  : mission.py

from Work.Classes import Function

functions = {
    'mission': Function(5, 1,
            'MISSION;server;crawler;order;hour;min','Time crawler to automatically run at hour:min every day')
}


import datetime


def deltatime(hour, min, sec=0):
    target_time = datetime.datetime(2017, 2, 18, hour, min, sec)
    current_time = datetime.datetime.now()
    return 86400 - ((current_time - target_time).seconds % 86400)


def waiter(order):
    timetowake = deltatime(int(order[3]), int(order[4]))
    while True:
        gv.mission_list[order[1]].event.wait(timetowake)
        if gv.mission_list[order[1]].event.isSet():
            break
        else:
            crawler(order)
            time.sleep(66)
            timetowake = deltatime(int(order[3]), int(order[4]))
    gv.mission_list[order[1]].event.clear()
    gv.mission_list[order[1]].state = 'Unsettled'
    return


def mission(order):
    if order[1] not in crawler_list and order[1] != "REFRESHER":
        return "No such cralwer!\n" \
               "Current cralwer:{}".format(str(crawler_list[1:-1]))
    if order[2].upper() == 'SET':
        if order[1] in gv.mission_list.keys() and gv.mission_list[order[1]].state == 'Settled':
            return "Mission has already settled"
        gv.mission_list[order[1]] = gv.Mission('Settled', order[3], order[4], threading.Event())
        threading.Thread(target=waiter, args=[order]).start()
        return "Successfully settled"
    elif order[2].upper() == 'CANCEL':
        if order[1] not in gv.mission_list.keys() or gv.mission_list[order[1]].state == 'Unsettled':
            return "Mission isn't running"
        gv.mission_list[order[1]].event.set()
        return "Successfully canceled"
    else:
        return "No such order!\n" \
               "you can set, cancel a mission."