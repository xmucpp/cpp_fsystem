# -*- coding: utf-8 -*-
# @Time  : 2017/3/25 16:04
# @Author: FSOL
# @File  : Crawler.py


class Worker:
    def __init__(self, event, table, state):
        self.event = event
        self.table = table
        self.state = state


def work(worker_name):
    logger.info('{}:worker start!'.format(worker_name))
    if worker_name == 'REFRESHER':
        logger.info('change time from {} to {}.'.format(cf.PRESENT_DAY, str(time.strftime('%Y-%m-%d', time.localtime(time.time())))))
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
            time.sleep(1)
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
               "Current cralwer:{}".format(str(crawler_list.keys()[1:-1]))
    if order[1] in gv.worker.keys() and gv.worker[order[1]].state == 'Running':
        return "Crawler {} is already running!".format(order[1])
    if order[1] not in gv.worker.keys():
        gv.worker[order[1]] = gv.Worker(threading.Event(), '------', 'Stopped')
    threading.Thread(target=work, args=[order[1]]).start()
    return "Crawler started!"