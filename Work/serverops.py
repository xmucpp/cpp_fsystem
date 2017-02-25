# -*- coding: utf-8 -*-
# @Author: FSOL
# @File  : serverops.py

import commands
import datetime
import select
import socket
import threading
import time
import json

import Crawler.FakeScraper as FakeScraper
import Crawler.JDPageScraper as JDPageScraper
import Crawler.TmallPageScraper as TmallPageScraper
import Crawler.Refresher as Refresher
from Work import globalvar as gv
import config as cf
from Work.log import Logger


logger = Logger('serverops', 'DEBUG')
def reloading():
    pass


def system(order):
    status, results = commands.getstatusoutput(order[1])
    if status == 0 and results != '':
        return results
    elif status == 0 and results == '':
        return "Success!\n"
    else:
        return 'ERROR:{}\n{}\n'.format(status, results)


def connect(order):
    try:
        order[2] = int(order[2])
    except Exception as e:
        return "port Error!{}".format(e)

    so = socket.socket()
    so.settimeout(5)
    try:
        so.connect((order[1], order[2]))
    except Exception as e:
        return 'IP Error!\n{}'.format(e)
    so.send(order[3])
    message = so.recv(1024)
    if message == cf.CONNECTCOMFIRM:
        so.settimeout(cf.timeout)
        gv.serverlist[so.fileno()] = so
        gv.epoll.register(so.fileno(), select.EPOLLIN)
        return cf.CONNECTSUCCESS
    else:
        so.close()
        return message


def shutdown(order):
    if [i.state for i in gv.worker.values()].count('Running'):
        return "Please kill all running work before shut down the server!"
    gv.order_to_close = True
    return "Server is shutting down."


def update(order):
    status, results = commands.getstatusoutput('git pull')
    if status == 0:
        gv.order_to_update = True
        return results
    else:
        return 'Update failed...\n{}  {}'.format(status, results)


def jsinfo(order):
    info_data = json.dumps({'sl': len(gv.serverlist),
                 'cl': len(gv.console),
                 'ul': len(gv.unidentified),
                 'wk': {work: {'s': gv.worker[work].state,
                         't': gv.worker[work].table, 'c': gv.crawlerstatis[work]} for work in gv.worker.keys()},
                 'ms': {mission: {'s': gv.mission_list[mission].state,
                         'h': gv.mission_list[mission].hour, 'm': gv.mission_list[mission].minute}
                        for mission in gv.mission_list.keys()}
                           })
    return info_data


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


def statistics(order):
    info_data = '\nConnected Server:{}'.format(len(gv.serverlist))
    info_data += '\nConnected Console:{}'.format(len(gv.console))
    info_data += '\nUnidentified Request:{}'.format(len(gv.unidentified))
    info_data += '\nCurrent worker:{}'.format(len(gv.worker))
    info_data += '\nCurrent mission:{}\n'.format(len(gv.mission_list))
    return info_data


def work(worker_name):
    logger.info('{}:worker start!'.format(worker_name))
    if worker_name == 'REFRESHER':
        cf.PRESENT_DAY = str(time.strftime('%Y-%m-%d', time.localtime(time.time())))
        for work in gv.worker.keys():
            logger.info('{} number:{}'.format(work, gv.crawlerstatis[work]))
            gv.crawlerstatis[work] = 0
        for title in crawler_list:
            try:
                if gv.redis.exists(title):
                    logger.error("{} still have unfinished data!".format(title))
                btitle = '{}{}'.format(cf.BACKUP, title)
                while gv.redis.exists(btitle):
                    gv.redis.lpush(title, gv.redis.blpop(btitle)[1])
            except Exception:
                logger.error(logger.traceback())
        logger.info("{} worker out".format(worker_name))
        return
    gv.worker[worker_name].state = 'Running'
    try:
        btitle = '{}{}'.format(cf.BACKUP, worker_name)
        while gv.redis.exists(worker_name):
            if gv.worker[worker_name].event.isSet():
                break
            try:
                gv.worker[worker_name].table = gv.redis.blpop(worker_name)[1]
                gv.redis.lpush(btitle, gv.worker[worker_name].table)

                if not crawler_list[worker_name].parse(gv.worker[worker_name].table):
                    gv.crawlerstatis[worker_name] += 1
                else:
                    logger.warning(gv.worker[worker_name].table)
            except Exception, e:
                logger.error(logger.traceback())
    except Exception as e:
        logger.error(logger.traceback())
    finally:
        gv.worker[worker_name].event.clear()
        logger.info("{} worker out".format(worker_name))
        gv.worker[worker_name].state = 'Stopped'


crawler_list = {'TMALL': TmallPageScraper,
                'JD': JDPageScraper,
                'FAKE': FakeScraper,
                }


def crawler(order):
    if order[1] == "REFRESHER":
        threading.Thread(target=work, args=[order[1]]).start()
        return "REFRESHING!"
    if order[1] not in crawler_list.keys():
        return "No such cralwer!\n" \
               "Current cralwer:{}".format(str(crawler_list[1:-1]))
    if order[1] in gv.worker.keys() and gv.worker[order[1]].state == 'Running':
        return "Crawler {} is already running!".format(order[1])
    if order[1] not in gv.worker.keys():
        gv.worker[order[1]] = gv.Worker(threading.Event(), '------', 'Stopped')
    threading.Thread(target=work, args=[order[1]]).start()
    return "Crawler started!"


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


def cancel(order):
    if order[1] not in crawler_list or gv.worker[order[1]].state != "Running":
        return "not cancelable"
    gv.worker[order[1]].event.set()
    return "Successfully canceled"


arguments_number = {'SYSTEM': 2, 'CONNECT': 4, 'INFO': 1, 'JSINFO': 1,
                    'STATISTICS': 1, 'CRAWLER': 2,
                    'SHUTDOWN': 1, 'UPDATE': 1, 'MISSION': 5, 'CANCEL': 2}
server_operation = {'SYSTEM': system, 'CONNECT': connect, 'INFO': info, 'JSINFO': jsinfo,
                    'STATISTICS': statistics, 'CRAWLER': crawler,
                    'SHUTDOWN': shutdown, 'UPDATE': update, 'MISSION': mission, 'CANCEL': cancel}


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
