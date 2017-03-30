# -*- coding: utf-8 -*-
# @Time  : 2017/3/30 20:11
# @Author: FSOL
# @File  : infos.py
import time
import Work.globalvar as gv
import mission as ms
import crawler


def info(order):
    info_data = 'Connections:{}\n'.format(len(gv.connections))
    for (fileno, conn) in gv.connections():
        peername = conn.socket.getpeername()
        info_data += "%-4d      %-12s     %-5d     %-10s     %-6s\n" % \
                     (fileno, peername[0], peername[1], conn.level, time.asctime(time.localtime(conn.time)))

    info_data += '\n---Current worker:{}\n'.format(len(crawler.worker_list))
    for (name, worker) in crawler.worker_list:
        info_data += "%-8s      %-8s     %-40s     %-8d\n" % \
                    (name, worker.state, worker.table, worker.count)

    info_data += '\n---Current mission:{}\n'.format(len(ms.mission_list))
    for (name, mission) in ms.mission_list:
        info_data += "%-8s      %-2s:%-2s     %-10s\n" %\
                     (name, mission.hour, mission.minute, mission.order)

    return info_data

functions = {
    'info': {'entry': info, 'argu_num': 0, 'dis_mode': 1,
             'way_to_use': 'INFO;server',
             'help_info': 'Check the situation of some servers',
             'collect': None}
}

