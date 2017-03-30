# -*- coding: utf-8 -*-
# @Time  : 2017/3/30 19:50
# @Author: FSOL
# @File  : crawler.py


import threading
import redis
import Subfunc.Crawler as Crawler
reload(Crawler)

import config as cf
from Work.log import Logger
logger = Logger('Crawler', 'DEBUG')
my_redis = redis.Redis(cf.RedisServer, port=cf.RedisPort, password=cf.RedisPass)

class Worker:
    def __init__(self, event, table, state, count=0):
        self.event = event
        self.table = table
        self.state = state
        self.count = count

worker_list = {}


def work(worker_name):
    logger.info('{}:worker start!'.format(worker_name))
    worker_list[worker_name].state = 'Running'
    try:
        btitle = '{}{}'.format(cf.BACKUP, worker_name)
        while my_redis.exists(worker_name):
            if worker_list[worker_name].event.isSet():
                break
            try:
                worker_list[worker_name].table = my_redis.blpop(worker_name)[1]
                my_redis.lpush(btitle, worker_list[worker_name].table)

                results = Crawler.crawler_list[worker_name].parse(worker_list[worker_name].table)
                if not results:
                    worker_list[worker_name].count += 1
                else:
                    logger.error(worker_list[worker_name].table)
                    break
            except Exception, e:
                logger.error(logger.traceback())
    except Exception as e:
        logger.error(logger.traceback())
    finally:
        worker_list[worker_name].event.clear()
        logger.info("{} worker out".format(worker_name))
        worker_list[worker_name].state = 'Stopped'


def crawler(order):
    """
    :param order:order[0]:start / stop, order[1]:crawler
    :return:
    """
    if order[1] not in Crawler.crawler_list:
        return "No such cralwer!\n" \
               "Current cralwer:{}".format(str(Crawler.crawler_list.keys())[1:-1])

    if order[0].upper() == 'START':
        if order[1] not in worker_list:
            worker_list[order[1]] = Worker(threading.Event(), '------', 'Stopped')
            threading.Thread(target=work, args=[order]).start()
            return "Successfully settled"
        elif worker_list[order[1]].state == 'Running':
            return "Crawler {} is already running!".format(order[1])
        else:
            threading.Thread(target=work, args=[order]).start()
            return "Successfully settled"

    elif order[0].upper() == 'STOP':
        if order[1] not in worker_list or worker_list[order[1]].state == 'Stopped':
            return "Crawler {} is not running!".format(order[1])
        else:
            worker_list[order[1]].event.set()
            return "Successfully stopped"
    else:
        return "No such order!\n" \
               "you can either start or cancel a crawler."

functions = {
    'crawler': {'entry': crawler, 'argu_num': 2, 'dis_mode': 1,
            'way_to_use': 'CRAWLER;server;order;crawler',
            'help_info': 'Start/Stop a cralwer one some machines.',
            'collect': None}
}
