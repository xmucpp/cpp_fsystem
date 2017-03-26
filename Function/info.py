# -*- coding: utf-8 -*-
# @Time  : 2017/3/25 16:06
# @Author: FSOL
# @File  : info.py



def info(order):
    info_data = 'Connected Server:{}\n'.format(len(gv.serverlist))
    for (fileno, server) in gv.serverlist.items():
        peername = server.getpeername()
        info_data += "%-4d      %-12s     %-5d     \n" % (fileno, peername[0], peername[1])
    info_data += '\nConnected Console:{}\n'.format(len(gv.console))
    for (fileno, con) in gv.console.items():
        peername = con.getpeername()
        info_data += "%-4d      %-12s     %-5d     \n" % (fileno, peername[0], peername[1])
    info_data += '\nUnidentified Request:{}\n'.format(len(gv.unidentified))
    for (fileno, uni) in gv.unidentified.items():
        peername = uni[1].getpeername()
        info_data += "%-4d      %-12s     %-5d     %-5.0f\n" % (fileno, peername[0], peername[1], time.time()-uni[0])
    info_data += '\n---Current worker:{}\n'.format(len(gv.worker))
    for work in gv.worker.keys():
        info_data += "%-8s      %-8s     %-40s     %-8d\n" % \
                    (work, gv.worker[work].state, gv.worker[work].table, gv.crawlerstatis[work])
    info_data += '\n---Current mission:{}\n'.format(len(gv.mission_list))
    for mission in gv.mission_list.keys():
        info_data += "%-8s      %-8s     %-2s:%-2s\n" %\
                     (mission, gv.mission_list[mission].state, gv.mission_list[mission].hour, gv.mission_list[mission].minute)
    return info_data