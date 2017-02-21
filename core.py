# git clone https://github.com/sinnfashen/New_web
# -*- coding: utf-8 -*-
# @Author: FSOL
# @File  : core.py

import socket
import select
import time
import hashlib

import Work.serverops as serverops
import Work.consoleops as consoleops
import globalvar as gv


def reloading():
    try:
        reload(serverops)
        serverops.reloading()
        reload(consoleops)
        consoleops.reloading()
    except Exception as e:
        print 'Reload after update error!{}'.format(e)
    finally:
        gv.order_to_update = False


def encry(password):
    return hashlib.md5(password).hexdigest()


def main():

    self = socket.socket()
    self.bind((gv.HOST, gv.PORT))
    self.listen(10)

    gv.epoll.register(self.fileno(), select.EPOLLIN)
    print "--------------------------------\n       SYSTEM STARTED"

    while True:
        if gv.order_to_close:
            break
        if gv.order_to_update:
            reloading()

        events = gv.epoll.poll(20)
        for fileno, event in events:
            if fileno == self.fileno():
                con, conaddr = self.accept()
                print conaddr, "Incoming Connection"
                gv.epoll.register(con.fileno(), select.EPOLLIN)
                gv.unidentified[con.fileno()] = [time.time(), con]

            elif fileno in gv.unidentified:
                message = gv.unidentified[fileno][1].recv(1024)
                if encry(message) == gv.CONNECTPASSWORD:
                    gv.serverlist[fileno] = gv.unidentified[fileno][1]
                    gv.unidentified.pop(fileno)
                    gv.serverlist[fileno].send(gv.CONNECTCOMFIRM)
                    print '{}: {}----server connected'.format(fileno, gv.serverlist[fileno].getpeername())
                elif encry(message) == gv.CONSOLEPASSWORD:
                    gv.console[fileno] = gv.unidentified[fileno][1]
                    gv.unidentified.pop(fileno)
                    gv.console[fileno].send(gv.CONNECTCOMFIRM)
                    print '{}: {}----console connected'.format(fileno, gv.console[fileno].getpeername())
                elif message == '':
                    print '{}: {}----unidentified disconnected'.format(fileno, gv.unidentified[fileno][1].getpeername())
                    gv.epoll.modify(fileno, 0)
                    gv.unidentified.pop(fileno)
                else:
                    gv.unidentified[fileno][1].send("WRONG PASSWORD!")
                    print '{}: {}----unidentified tried a wrong password'\
                        .format(fileno, gv.unidentified[fileno][1].getpeername())

            elif fileno in gv.console:
                message = gv.console[fileno].recv(1024)
                print "message from console {}:\n{}".format(fileno, message)
                if message == '':
                    gv.epoll.modify(fileno, 0)
                    gv.console.pop(fileno)
                else:
                    gv.console[fileno].sendall(consoleops.console_order(message))

            elif fileno in gv.serverlist:
                message = gv.serverlist[fileno].recv(1024)
                print "message from server{}:\n{}".format(fileno, message)
                if message == '':
                    gv.epoll.modify(fileno, 0)
                    gv.serverlist.pop(fileno)
                else:
                    gv.serverlist[fileno].sendall(serverops.server_order(message))

            else:
                print "what?"

        for (fileno, uni) in gv.unidentified.items():
            if time.time() - uni[0] >= gv.OUTTIME:
                cli = uni[1]
                cli.send("auto disconnect\n")
                gv.unidentified.pop(cli.fileno())
                cli.close()

    print "Server is shutting down......"
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
