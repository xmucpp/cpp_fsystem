import commands
import threading
import socket
import time
import globalvar as gv
import Crawler.TmallPageScraper as TmallPageScraper


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
    gv.BUFFER = so.recv(1024)
    if gv.BUFFER == gv.CONNECTCOMFIRM:
        gv.serverlist[so.fileno()] = so
        return gv.CONNECTSUCCESS
    else:
        return gv.BUFFER


def shutdown(order):
    if gv.workerstate.values().count('Running'):
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
    info_data += '\n---Current worker:{}\n'.format(gv.workerstate.values().count('Running'))
    for work in gv.worker.keys():
        info_data += "%-8s      %-8s     %-40s     %-8d\n" % \
                    (work, gv.workerstate[work], gv.worktable[work], gv.crawlerstatis[work])
    return info_data


def statistics(order):
    info_data = '\nConnected Server:{}'.format(len(gv.serverlist))
    info_data += '\nConnected Console:{}'.format(len(gv.console))
    info_data += '\nUnidentified Request:{}'.format(len(gv.unidentified))
    info_data += '\nCurrent worker:{}\n'.format(gv.workerstate.values().count('Running'))
    return info_data


def worker(target_web):
    gv.workerstate[target_web] = 'Running'
    try:
        while gv.redis.exists(target_web):
            try:
                gv.worktable[target_web] = gv.redis.blpop(target_web)
            except Exception as e:
                print e
            gv.redis.lpush('{}{}'.format(gv.BACKUP, target_web), gv.worktable)
            crawler_list[target_web].parse(gv.worktable[target_web])
            gv.crawlerstatis[target_web] += 1
    except Exception as e:
        print e
    finally:
        gv.workerstate[target_web] = 'Stopped'


crawler_list = {'TMALL': TmallPageScraper}


def crawler(order):
    if order[1] not in crawler_list.keys():
        return "No such cralwer!\n" \
               "Current cralwer:{}".format(str(crawler_list[1:-1]))
    if order[1] in gv.worker.keys():
        return "Crawler {} is already running!".format(order[1])

    gv.worker[order[1]] = threading.Thread(target=worker, args=order[1])
    gv.worker[order[1]].start()
    return "Crawler started!"


arguments_number = {'SYSTEM': 2, 'CONNECT': 3, 'INFO': 1,
                    'STATISTICS': 1, 'CRAWLER': 2,
                    'SHUTDOWN': 1}
server_operation = {'SYSTEM': system, 'CONNECT': connect, 'INFO': info,
                    'STATISTICS': statistics, 'CRAWLER': crawler,
                    'SHUTDOWN': shutdown, 'UPDATE': update}


def server_order(message):
    if message.find(gv.ORDER) == -1:
        order = [message]
    else:
        order = message.split(gv.ORDER)
    if len(order) != arguments_number[order[0]]:
        return "wrong arguments"
    return server_operation[order[0]](order)
