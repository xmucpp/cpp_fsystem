# git clone https://github.com/sinnfashen/New_web
# -*- coding: utf-8 -*-
# @Author: FSOL
# @File  : core.py

"""
core.py
========================
As its name, the core.py is the center of the whole system.
It is mainly in charge of connection management.(i.e. receive connection requests and messages and reply)

It has 2 modes(for now） to start: soldier and king.
(more information about modes or others can be found in the link in read_me)

To start in king mode, just type 'python core.py' and it will use the localhost in config to listen
preparing to receive connections or else.

To start in soldier mode, you should add target ip:host and password for server like this
'python core.py 127.0.0.1 9999 password'
and it will automatically connect to the server you said and try ONE time with the password,
If password is wrong, it will exit. Except for that, it will start to wait for order from target server.
(Both can use nohup or & or ...)

    Be aware that I use fileno to identify a connection,
    and the connections are stored in the globalvar.py.
"""
import hashlib
import select
import socket
import time
import sys
import threading

import Work.distributor as distributor
import Work.serverops as serverops
import Work.globalvar as gv
import config as cf
from Work.log import Logger


logger = Logger('core', 'DEBUG')
self = socket.socket()
password_list = dict(zip(cf.user_password.values(), cf.user_password.keys()))
# punish_list is record of times of wrong password, being used to avoid someone try the password too many times.
# link_list is record of times of connection of one ip address, also being used to anti-attack.
punish_list = {}
link_list = {}


def reloading():
    """
    reload files after update to keep all files are up-to-date.
    (Won't reload globalvar client and log)
    :return:
    """
    try:
        reload(serverops)
        serverops.reloading()
        reload(distributor)
        distributor.reloading()
        reload(cf)
    except Exception as e:
        logger.error('Reload after update error!{}'.format(e))
    finally:
        gv.order_to_update = False


def encry(password):
    """
    md5
    :param password:
    :return: md5(password)
    """
    return hashlib.md5(password).hexdigest()


def disconnect(fileno):
    """
    Standard way to disconnect and clean all stuff without risk.
    :param fileno:
    :return:
    """
    logger.info('{}:----{} disconnected'.format(gv.connections[fileno].level, fileno))
    if gv.connections[fileno].level == 'Unidentified':
        gv.outside.modify(fileno, 0)
    else:
        gv.inside.modify(fileno, 0)
    gv.connections[fileno].socket.close()
    gv.connections.pop(fileno)
    punish_list[fileno] = 0


def save_send(fileno, message):
    """
    Standard way to send message.
    Avoid the risk of socket closed before send.(In that case, log and disconnect with it)
    :param fileno:
    :param message:
    :return: 0 for normal and 1 for error.
    """
    try:
        gv.connections[fileno].socket.sendall(message)
    except Exception:
        logger.warning("{}: close before send.".format(fileno))
        disconnect(fileno)
        return 1
    return 0


def upgrade(fileno, level):
    """
    Give the connection level after received corresponding password.(Disconnect if it closed while logging or sending)
    :param fileno:
    :param level:
    :return:
    """
    gv.connections[fileno].level = level
    gv.epoll.register(fileno, select.EPOLLIN)
    gv.outside.modify(fileno, 0)
    if save_send(fileno, cf.CONNECTSUCCESS) == 1:
        return 1
    try:
        logger.info('{}: {}----{} connected'.format(fileno, gv.connections[fileno].socket.getpeername()))
    except Exception:
        logger.warning("{}: unexcepted close.".format(fileno))
        disconnect(fileno)
    return 0


def punishment(fileno):
    """
    If fileno entered x times wrong password, it has to wait x^2 seconds to be heard again,
    but if x is bigger than 10, just disconnect.
    :param fileno:
    :return:
    """
    gv.outside.modify(fileno, 0)
    if punish_list[fileno] <= 10:
        time.sleep(punish_list[fileno]*punish_list[fileno])
        save_send(fileno, "WRONG PASSWORD!")
    else:
        save_send(fileno, "Enough!")
        disconnect(fileno)


def addcount(fileno, the_list):
    if fileno in the_list:
        the_list[fileno] += 1
    else:
        the_list[fileno] = 1


def kill_out_time():
    """
    Check all connections and disconnect with those being unidentified for too long(OUTTIME in config).
    :return:
    """
    for (fileno, conn) in gv.connections.items():
        if conn.level == 'Unidentified' and time.time() - conn.time >= cf.OUTTIME:
            save_send(fileno, "auto disconnect\n")
            disconnect(fileno)


def outside_listen():
    """
    Listen from new and unidentified connections.
    :return:
    """
    while True:
        events = gv.outside.poll(20)
        for fileno, event in events:
            try:
                if fileno == self.fileno():
                    con, conaddr = self.accept()
                    if link_list[conaddr[0]] <= 20:
                        logger.info(' '.join([str(conaddr), "Incoming Connection"]))
                        addcount(fileno, link_list)
                        gv.outside.register(con.fileno(), select.EPOLLIN)
                        gv.connections[con.fileno()] = gv.connections(con, time.time())
                else:
                    try:
                        message = gv.connections[fileno].socket.recv(1024)
                    except Exception:
                        message = ''
                    if message == '':
                        disconnect(fileno)
                    elif encry(message) in password_list:
                        upgrade(fileno, password_list[encry(message)])
                    else:
                        addcount(fileno, punish_list)
                        threading.Thread(target=punishment, args=[fileno]).start()
                        try:
                            logger.info('{}: {}----unidentified tried a wrong password' \
                                        .format(fileno, gv.connections[fileno].socket.getpeername()))
                        except Exception:
                            logger.warning("{}: unexcepted close.".format(fileno))
                            disconnect(fileno)
            except Exception:
                logger.error(logger.traceback())


def event_divider():
    """
    Listen from identified connections.
    :return:
    """
    events = gv.inside.poll(20)
    for fileno, event in events:
        try:
            message = gv.connections[fileno].socket.recv(1024)
        except Exception:
            message = ''
        logger.info("message from {} {}:{}".format(gv.connections[fileno].level, fileno, message))
        if message == '':
            disconnect(fileno)
        else:
            save_send(fileno, distributor.console_order(message))


def master_server():
    socket.setdefaulttimeout(cf.timeout)
    self.bind((cf.HOST, cf.PORT))
    self.listen(10)
    gv.outside.register(self.fileno(), select.EPOLLIN)
    threading.Thread(target=outside_listen, args=[]).start()
    logger.info("--------------------------------\n          MASTER SYSTEM STARTED")
    while True:
        if gv.order_to_close:
            break
        if gv.order_to_update:
            reloading()
        event_divider()
        kill_out_time()


def soldier_server():
    global self
    if len(sys.argv) == 2:
        self.connect(cf.master)
    else:
        self.connect((sys.argv[2], int(sys.argv[3])))
    logger.info("--------------------------------\n          SOLDIER SYSTEM STARTED")
    self.send(sys.argv[1])
    message = self.recv(1024)
    logger.info(message)
    if message != cf.CONNECTSUCCESS:
        return 0
    while True:
        try:
            if gv.order_to_close:
                break
            if gv.order_to_update:
                reloading()
            message = self.recv(1024)
            respond = distributor.server_order(message)
            if respond:
                self.send(respond)
            else:
                self.send("empty")
        except Exception:
            logger.error(logger.traceback())
            logger.error("Lost connection, retry in 5min")
            time.sleep(300)
            self = socket.socket()


def main():
    try:
        if len(sys.argv) != 1:
            soldier_server()
        else:
            master_server()
    except Exception:
        logger.error(logger.traceback())
    finally:
        logger.info("Server is shutting down......")
        for fileno in gv.connections:
            disconnect(fileno)
        self.close()
    return 0


if __name__ == "__main__":
    main()
