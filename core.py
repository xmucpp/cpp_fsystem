# git clone https://github.com/sinnfashen/New_web
# -*- coding: utf-8 -*-
# @Author: FSOL
# @File  : core.py

import hashlib
import select
import socket
import time
import sys

import Work.consoleops as consoleops
import Work.serverops as serverops
import Work.globalvar as gv
import config as cf
from Work.log import Logger


logger = Logger('core', 'DEBUG')
self = socket.socket()
des_list = {'server': gv.serverlist, 'console': gv.console}


def reloading():
    try:
        reload(serverops)
        serverops.reloading()
        reload(consoleops)
        consoleops.reloading()
        reload(cf)
    except Exception as e:
        logger.error('Reload after update error!{}'.format(e))
    finally:
        gv.order_to_update = False


def encry(password):
    return hashlib.md5(password).hexdigest()


def save_send(sock, fileno, message):
    try:
        sock.sendall(message)
    except Exception:
        logger.warning("{}: close before send.".format(fileno))
        return 1
    return 0


def upgrade(fileno, des):
    des_list[des][fileno] = gv.unidentified[fileno][1]
    gv.unidentified.pop(fileno)
    if save_send(des_list[des][fileno], fileno, cf.CONNECTCOMFIRM) == 1:
        return 1
    try:
        logger.info('{}: {}----{} connected'.format(fileno, des_list[des][fileno].getpeername(), des))
    except Exception:
        logger.warning("{}: unexcepted close.".format(fileno))
    return 0


def event_divider():
    events = gv.epoll.poll(20)
    for fileno, event in events:
        if fileno == self.fileno():
            con, conaddr = self.accept()
            logger.info(' '.join([str(conaddr), "Incoming Connection"]))
            gv.epoll.register(con.fileno(), select.EPOLLIN)
            gv.unidentified[con.fileno()] = [time.time(), con]

        elif fileno in gv.unidentified:
            try:
                message = gv.unidentified[fileno][1].recv(1024)
            except Exception:
                message = ''
            if message == '':
                logger.info('{}:----unidentified disconnected'.format(fileno))
                gv.epoll.modify(fileno, 0)
                gv.unidentified.pop(fileno)
            elif encry(message) == cf.CONNECTPASSWORD:
                upgrade(fileno, 'server')
            elif encry(message) == cf.CONSOLEPASSWORD:
                upgrade(fileno, 'console')
            elif encry(message) == cf.WEBPASSWORD:
                save_send(gv.unidentified[fileno][1], fileno, consoleops.console_order('jsinfo'))
                gv.epoll.modify(fileno, 0)
                gv.unidentified.pop(fileno)
            else:
                save_send(gv.unidentified[fileno][1], fileno, "WRONG PASSWORD!")
                try:
                    logger.info('{}: {}----unidentified tried a wrong password' \
                            .format(fileno, gv.unidentified[fileno][1].getpeername()))
                except Exception:
                    logger.warning("{}: unexcepted close.".format(fileno))

        elif fileno in gv.console:
            try:
                message = gv.console[fileno].recv(1024)
            except Exception:
                message = ''
            logger.info("message from console {}:{}".format(fileno, message))
            if message == '':
                gv.epoll.modify(fileno, 0)
                gv.console.pop(fileno)
            else:
                save_send(gv.console[fileno], fileno, consoleops.console_order(message))

        elif fileno in gv.serverlist:
            try:
                message = gv.serverlist[fileno].recv(1024)
            except Exception:
                message = ''
            logger.info("message from server{}:{}".format(fileno, message))
            if message == '':
                gv.epoll.modify(fileno, 0)
                gv.serverlist.pop(fileno)
            else:
                respond = consoleops.server_order(message)
                if respond != '':
                    save_send(gv.serverlist[fileno], fileno, respond)
        else:
            logger.critical("what?")


def kill_out_time():
    for (fileno, uni) in gv.unidentified.items():
        if time.time() - uni[0] >= cf.OUTTIME:
            cli = uni[1]
            try:
                cli.send("auto disconnect\n")
            except Exception:
                logger.warning("{}: close before send.".format(fileno))
            gv.unidentified.pop(cli.fileno())
            cli.close()


def master_server():
    self.bind((cf.HOST, cf.PORT))
    self.listen(10)
    gv.epoll.register(self.fileno(), select.EPOLLIN)
    logger.info("--------------------------------\n          MASTER SYSTEM STARTED")
    while True:
        if gv.order_to_close:
            break
        if gv.order_to_update:
            reloading()
        event_divider()
        kill_out_time()


def slave_server():
    if len(sys.argv) == 2:
        self.connect(cf.master)
    else:
        self.connect((sys.argv[2], int(sys.argv[3])))
    logger.info("--------------------------------\n          SLAVE SYSTEM STARTED")
    self.send(sys.argv[1])
    logger.info(self.recv(1024))
    while True:
        try:
            if gv.order_to_close:
                break
            if gv.order_to_update:
                reloading()
            message = self.recv(1024)
            respond = consoleops.server_order(message)
            if respond:
                self.send(respond)
            else:
                self.send("empty")
        except Exception:
            logger.error(logger.traceback())
            logger.error("Lost connection, retry in 5min")
            time.sleep(300)


def main():
    try:
        if len(sys.argv) != 1:
            slave_server()
        else:
            master_server()
    except Exception:
        logger.error(logger.traceback())
    finally:
        logger.info("Server is shutting down......")
        for (fileno, server) in gv.serverlist.items():
            server.close()
        for (fileno, con) in gv.console.items():
            con.close()
        for (fileno, uni) in gv.unidentified.items():
            uni[1].close()
        self.close()
    return 0


if __name__ == "__main__":
    main()
