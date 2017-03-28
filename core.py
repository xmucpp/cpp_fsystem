# -*- coding: utf-8 -*-
# @Author: FSOL
# @File  : core.py

"""
core.py
========================
As its name, the core.py is the center of the whole system.
It is mainly in charge of connection management.(i.e. receive connection requests and messages and reply)

It has 2 modes(for now） to start: soldier and king.
    (just as the slave and master model,
    I name them like this just for fun and some possible update about connection model.)

To start in king mode, just type 'python core.py' and it will use the localhost in config to listen
preparing to receive connections or else.

To start in soldier mode, you should add target ip:host and password for server like this
'python core.py 127.0.0.1 9999 password'
and it will automatically connect to the server you said and try ONE time with the password,
If password is wrong, it will exit. Except for that, it will start to wait for order from target server.
(Both can use nohup or & or ...)

    Be aware that I use fileno to identify a connection,
    and connections are stored in the globalvar.py.

url to this system: https://github.com/sinnfashen/New_web
"""
import hashlib
import select
import socket
import time
import sys
import threading

import Work.globalvar as gv
import config as cf
from Work.log import Logger

# Initialize
import Function
import User

logger = Logger('connection', 'DEBUG')
inside = select.epoll()
outside = select.epoll()
password_list = dict(zip(cf.user_password.values(), cf.user_password.keys()))
self = socket.socket()
# punish_list is record of times of wrong password, being used to avoid someone try the password too many times.
# link_list is record of times of connection of one ip address, also being used to anti-attack.
punish_list = {}
link_list = {}


class Connection:
    logger = Logger('connection', 'DEBUG')

    def __init__(self, fileno, socket, time, level='Unidentified'):
        self.fileno = fileno
        self.socket = socket
        self.level = level
        self.time = time

    def disconnect(self):
        """
        Standard way to disconnect and clean all stuff without risk.
        :param self:
        :return:
        """
        User.user_list[self.level]['leave']()
        self.logger.info('{}:----{} disconnected'.format(self.fileno, self.level))
        if self.level == 'Unidentified':
            outside.modify(self.fileno, 0)
        else:
            inside.modify(self.fileno, 0)
        self.socket.close()
        gv.connections.pop(self.fileno)
        punish_list[self.fileno] = 0

    def save_send(self, message):
        """
        Standard way to send message.
        Avoid the risk of socket closed before send.(In that case, log and disconnect with it)
        :param self:
        :param message:
        :return: 0 for normal and 1 for error.
        """
        try:
            self.socket.sendall(message)
        except Exception:
            self.logger.warning("{}: close before send.".format(self.fileno))
            self.disconnect()
            return 1
        return 0

    def upgrade(self, level):
        """
        Give the connection level after received corresponding password.(Disconnect if it closed)
        :param self:
        :param level:
        :return:
        """
        link_list[self.socket.getpeername()] -= 1
        self.level = level
        inside.register(self.fileno, select.EPOLLIN)
        outside.modify(self.fileno, 0)
        if self.save_send(cf.CONNECTSUCCESS) == 1:
            return 1
        try:
            User.user_list[self.level]['entry']()
            self.logger.info('{}: {}----{} connected'.format(
                self.fileno, self.socket.getpeername(), self.level))
        except Exception:
            self.logger.warning("{}: {} unexcepted close.".format(self.fileno, self.level))
            self.disconnect()
        return 0

    def save_receive(self):
        """
        Standard way to receive a message.
        :return:
        """
        try:
            message = self.socket.recv(2048)
        except Exception:
            message = ''
        if message == '':
            self.disconnect()
        else:
            return message

    def process(self, message):
        return User.user_list[self.level]['receive'](self, message)


def reloading():
    """
    Reload files after update to keep all files are up-to-date.
    (Won't reload globalvar, client and log)
    :return:
    """
    Function.function_list.clear()
    User.user_list.clear()
    try:
        reload(Function)
        reload(User)
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


def punishment(conn):
    """
    If fileno has given x times wrong password, it has to wait x^2 seconds to be heard again,
    but if x is bigger than 10, just disconnect.

    This function is operated in a single threading so that won't affect other requests.
    :param conn: connection
    :return:
    """
    outside.modify(conn.fileno, 0)
    if punish_list[conn.fileno] <= 10:
        time.sleep(punish_list[conn.fileno]*punish_list[conn.fileno])
        conn.save_send("WRONG PASSWORD!")
    else:
        conn.save_send("Enough!")
        conn.disconnect()


def add_count(number, the_list):
    """
    Small function to make sure list start from 0.
    :param number:
    :param the_list:
    :return:
    """
    if number in the_list:
        the_list[number] += 1
    else:
        the_list[number] = 1


def kill_out_time():
    """
    Check all connections and disconnect with those being unidentified for too long(OUTTIME in config).
    :return:
    """
    for conn in gv.connections:
        if conn.level == 'Unidentified' and time.time() - conn.time >= cf.OUTTIME:
            conn.save_send("auto disconnect\n")
            conn.disconnect()


def outside_listen():
    """
    Listen from new and unidentified connections.
    :return:
    """
    while True:
        events = outside.poll(20)
        for fileno, event in events:
            try:
                if fileno == self.fileno():
                    con, conaddr = self.accept()
                    if conaddr not in link_list or link_list[conaddr[0]] <= 20:
                        add_count(conaddr[0], link_list)
                        logger.info(' '.join([str(conaddr), "Incoming Connection"]))
                        outside.register(con.fileno(), select.EPOLLIN)
                        gv.connections[con.fileno()] = Connection(con.fileno(), con, time.time())
                else:
                    conn = gv.connections[fileno]
                    message = conn.save_receive()
                    if message:
                        if encry(message) in password_list:
                            conn.upgrade(password_list[encry(message)])
                        else:
                            add_count(fileno, punish_list)
                            temp = threading.Thread(target=punishment, args=[conn])
                            temp.setDaemon(True)
                            temp.start()
                            try:
                                logger.info('{}: {}----unidentified tried a wrong password'
                                        .format(fileno, conn.socket.getpeername()))
                            except Exception:
                                logger.warning("{}: unexcepted close.".format(fileno))
                                conn.disconnect()
            except Exception:
                logger.error(logger.traceback())


def event_divider():
    """
    Listen from identified connections.
    Be aware that unlike soldier, king won't respond if there is nothing to say.
    :return:
    """
    events = inside.poll(20)
    for fileno, event in events:
        conn = gv.connections[fileno]
        message = conn.save_receive()
        if message:
            conn.save_send(conn.pre_process(message))


def king_server():
    """
    Server starting in king mode will split one threading to receive unidentified connections
        and handle the others itself.
    How long will one loop be depends on any information received, which will cause a immediately flush.
    But it will finished at least in 20s.
    :return:
    """
    socket.setdefaulttimeout(cf.timeout)
    self.bind((cf.HOST, cf.PORT))
    self.listen(10)
    outside.register(self.fileno(), select.EPOLLIN)
    tout = threading.Thread(target=outside_listen, args=[])
    tout.setDaemon(True)
    tout.start()
    logger.info("--------------------------------\n          MASTER SYSTEM STARTED")
    while True:
        if gv.order_to_close:
            break
        if gv.order_to_update:
            reloading()
        event_divider()
        kill_out_time()


def soldier_server():
    """
    Since soldier should only maintain one connection with king, there is no need for a object of connection or epoll.
    If only password was passed in, connect default_king set in config.py.
    Otherwise connect the ip:port passed in.
    Soldier will stop trying only when the password was rejected.

    Whether the order is correct(which should be in most cases), soldier will respond one time for one order, where
        respond can be 'empty' for 'nothing to say'.
    :return:
    """
    global self
    while True:
        self = socket.socket()
        try:
            if len(sys.argv) == 2:
                self.connect(cf.default_king)
            else:
                self.connect((sys.argv[2], int(sys.argv[3])))
            logger.info("--------------------------------\n          SOLDIER SYSTEM STARTED")
            self.send(sys.argv[1])
            message = self.recv(1024)
        except Exception:
            logger.error(logger.traceback())
            logger.error("Lost connection, retry in 5min")
            self.close()
            time.sleep(300)
            continue
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
                respond = User.user_list['server']['receive'](message)
                if respond:
                    self.send(respond)
                else:
                    self.send("empty")
            except Exception:
                logger.error(logger.traceback())
                logger.error("Lost connection, retry in 5min")
                self.close()
                time.sleep(300)
                break


def main():
    """
    Choose the mode.
    The arguments are like this:
    python core.py[0] password[1] ip[2] port[3]
    :return:
    """
    try:
        if len(sys.argv) != 1:
            soldier_server()
        else:
            king_server()
    except Exception:
        logger.error(logger.traceback())
    finally:
        logger.info("Server is shutting down......")
        for fileno in gv.connections:
            gv.connections[fileno].disconnect()
        self.close()
    return 0


if __name__ == "__main__":
    main()
