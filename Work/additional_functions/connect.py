# -*- coding: utf-8 -*-
# @Time  : 2017/3/25 16:06
# @Author: FSOL
# @File  : connect.py

import socket
import config as cf
import Work.globalvar as gv


def connect(order):
    try:
        order[1] = int(order[1])
    except Exception as e:
        return "port Error!{}".format(e)

    so = socket.socket()
    so.settimeout(5)
    try:
        so.connect((order[0], order[1]))
    except Exception as e:
        return 'IP or port Error!\n{}'.format(e)
    so.send(order[2])
    message = so.recv(1024)
    if message == cf.CONNECTSUCCESS:
        so.settimeout(cf.timeout)
        gv.serverlist[so.fileno()] = so
        gv.epoll.register(so.fileno(), select.EPOLLIN)
        return cf.CONNECTSUCCESS
    else:
        so.close()
        return message

