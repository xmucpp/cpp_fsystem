import commands
import threading
import socket
import time
import select
import datetime
import globalvar as gv
import Crawler.TmallPageScraper as TmallPageScraper
import Crawler.JDPageScraper as JDPageScraper
import Crawler.FakeScraper as FakeScraper


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

    try:
        so.connect((order[1], order[2]))
    except Exception as e:
        return 'IP Error!\n{}'.format(e)
    so.send(gv.CONNECTPASSWORD)
    message = so.recv(1024)
    if message == gv.CONNECTCOMFIRM:
        gv.serverlist[so.fileno()] = so
        gv.epoll.register(so.fileno(), select.EPOLLIN)
        return gv.CONNECTSUCCESS
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
                    (work, gv.worker[work].state, gv.worker[work].table, gv.crawlerstatis[gv.worker[work].target])
    info_data += '\n---Current mission:{}\n'.format(len(gv.mission_list))
    for mission in gv.mission_list.keys():
        info_data += "%-8s      %-8s     %-2d:%-2d\n" %\
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
    gv.worker[worker_name].state = 'Running'
    try:
        while gv.redis.exists(worker_name):
            if gv.worker[worker_name].event.isSet():
                break
            try:
                gv.worker[worker_name].table = gv.redis.blpop(worker_name)[1]
                gv.redis.lpush('{}{}'.format(gv.BACKUP, worker_name, gv.worker[worker_name].table))

                if not crawler_list[worker_name].parse(gv.worker[worker_name].table):
                    gv.crawlerstatis[worker_name] += 1
                else:
                    print gv.worker[worker_name].table
            except Exception, e:
                print e
    except Exception as e:
        print e
    finally:
        gv.worker[worker_name].event.clear()
        print "{} worker out".format(gv.worker[worker_name].target)
        gv.worker[worker_name].state = 'Stopped'


crawler_list = {'TMALL': TmallPageScraper,
                'JD': JDPageScraper,
                'FAKE': FakeScraper}


def crawler(order):
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
    if order[1] not in crawler_list:
        return "No such cralwer!\n" \
               "Current cralwer:{}".format(str(crawler_list[1:-1]))
    if order[2].upper() == 'SET':
        if order[1] in gv.mission_list.keys() and gv.mission_list[order[1]].state == 'Settled':
            return "Mission has already settled"
        gv.mission_list[order[1]] = gv.Mission('Settled', order[3], order[4], threading.Event())
        t = threading.Thread(target=waiter, args=[order])
        t.run()
        return "Successfully settled"
    elif order[2].upper() == 'CANCEL':
        if order[1] not in gv.mission_list.keys() or not gv.mission_list[order[1]].state == 'Unsettled':
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


arguments_number = {'SYSTEM': 2, 'CONNECT': 3, 'INFO': 1,
                    'STATISTICS': 1, 'CRAWLER': 2,
                    'SHUTDOWN': 1, 'UPDATE': 1, 'MISSION': 5, 'CANCEL': 2}
server_operation = {'SYSTEM': system, 'CONNECT': connect, 'INFO': info,
                    'STATISTICS': statistics, 'CRAWLER': crawler,
                    'SHUTDOWN': shutdown, 'UPDATE': update, 'MISSION': mission, 'CANCEL': cancel}


def server_order(message):
    if message.find(gv.ORDER) == -1:
        order = [message]
    else:
        order = message.split(gv.ORDER)
    if order[0] not in server_operation.keys():
        return "what are you talking about?"
    if len(order) != arguments_number[order[0]]:
        return "wrong arguments"
    return server_operation[order[0]](order)
