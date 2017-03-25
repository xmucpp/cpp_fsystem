# -*- coding: utf-8 -*-
# @Time  : 2017/3/25 16:06
# @Author: FSOL
# @File  : connect.py


def connect(order):
    try:
        order[2] = int(order[2])
    except Exception as e:
        return "port Error!{}".format(e)

    so = socket.socket()
    so.settimeout(5)
    try:
        so.connect((order[1], order[2]))
    except Exception as e:
        return 'IP Error!\n{}'.format(e)
    so.send(order[3])
    message = so.recv(1024)
    if message == cf.CONNECTCOMFIRM:
        so.settimeout(cf.timeout)
        gv.serverlist[so.fileno()] = so
        gv.epoll.register(so.fileno(), select.EPOLLIN)
        return cf.CONNECTSUCCESS
    else:
        so.close()
        return message