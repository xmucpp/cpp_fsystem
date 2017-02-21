# git clone https://github.com/sinnfashen/New_web
# -*- coding: utf-8 -*-
# @Author: FSOL
# @File  : core.py

import hashlib
import select
import socket
import time

import Work.consoleops as consoleops
import Work.serverops as serverops
import Work.globalvar as gv
import config as cf
from Work.log import Logger


logger = Logger('core', 'DEBUG')


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


def main():
    self = socket.socket()
    try:
        self.bind((cf.HOST, cf.PORT))
        self.listen(10)

        gv.epoll.register(self.fileno(), select.EPOLLIN)
        logger.info("--------------------------------\n       SYSTEM STARTED")

        while True:
            if gv.order_to_close:
                break
            if gv.order_to_update:
                reloading()

            events = gv.epoll.poll(20)
            for fileno, event in events:
                if fileno == self.fileno():
                    con, conaddr = self.accept()
                    logger.info(' '.join([str(conaddr), "Incoming Connection"]))
                    gv.epoll.register(con.fileno(), select.EPOLLIN)
                    gv.unidentified[con.fileno()] = [time.time(), con]

                elif fileno in gv.unidentified:
                    message = gv.unidentified[fileno][1].recv(1024)
                    if encry(message) == cf.CONNECTPASSWORD:
                        gv.serverlist[fileno] = gv.unidentified[fileno][1]
                        gv.unidentified.pop(fileno)
                        gv.serverlist[fileno].send(cf.CONNECTCOMFIRM)
                        logger.info('{}: {}----server connected'.format(fileno, gv.serverlist[fileno].getpeername()))
                    elif encry(message) == cf.CONSOLEPASSWORD:
                        gv.console[fileno] = gv.unidentified[fileno][1]
                        gv.unidentified.pop(fileno)
                        gv.console[fileno].send(cf.CONNECTCOMFIRM)
                        logger.info('{}: {}----console connected'.format(fileno, gv.console[fileno].getpeername()))
                    elif message == '':
                        logger.info('{}: {}----unidentified disconnected'.format(fileno, gv.unidentified[fileno][1].getpeername()))
                        gv.epoll.modify(fileno, 0)
                        gv.unidentified.pop(fileno)
                    else:
                        gv.unidentified[fileno][1].send("WRONG PASSWORD!")
                        logger.info('{}: {}----unidentified tried a wrong password' \
                            .format(fileno, gv.unidentified[fileno][1].getpeername()))

                elif fileno in gv.console:
                    message = gv.console[fileno].recv(1024)
                    logger.info("message from console {}:\n{}".format(fileno, message))
                    if message == '':
                        gv.epoll.modify(fileno, 0)
                        gv.console.pop(fileno)
                    else:
                        gv.console[fileno].sendall(consoleops.console_order(message))

                elif fileno in gv.serverlist:
                    message = gv.serverlist[fileno].recv(1024)
                    logger.info("message from server{}:\n{}".format(fileno, message))
                    if message == '':
                        gv.epoll.modify(fileno, 0)
                        gv.serverlist.pop(fileno)
                    else:
                        gv.serverlist[fileno].sendall(serverops.server_order(message))

                else:
                    logger.critical("what?")

            for (fileno, uni) in gv.unidentified.items():
                if time.time() - uni[0] >= cf.OUTTIME:
                    cli = uni[1]
                    cli.send("auto disconnect\n")
                    gv.unidentified.pop(cli.fileno())
                    cli.close()

    except Exception, e:
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
