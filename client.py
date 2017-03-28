# -*- coding: utf-8 -*-
# @Author: FSOL
# @File  : client.py

"""
client.py
==================
Used as a default console to connect and control server.
Will only connect to local's server.
"""
import socket
import readline
import sys
import select


def communicate(server):
    epoll = select.epoll()
    epoll.register(server.fileno(), select.EPOLLHUP)
    user_input = raw_input('-->')
    while user_input != 'exit':
        events = epoll.poll(1)
        if events:
            break
        server.send(user_input)
        message = server.recv(4096)
        print message
        user_input = raw_input('-->')
        while user_input == '':
            user_input = raw_input('-->')
    server.close()
    if user_input == 'exit':
        return 1
    return 0


def main():
    flag = False
    print "---------------------------\n      Initializing....\n"
    user_input = ''
    while user_input != 'n':
        server = socket.socket()
        try:
            if len(sys.argv) != 1:
                server.connect(('127.0.0.1', int(sys.argv[1])))
            else:
                server.connect(('127.0.0.1', 9813))
            while True:
                user_input = raw_input("Please input the password to server(exit to close):")
                if user_input == 'exit':
                    flag = True
                    break
                server.send(user_input)
                message = server.recv(8192)
                if message == 'Connection established':
                    print "Connection established."
                    if communicate(server):
                        flag = True
                        break
                    print "Disconnected."
                else:
                    print "Connection refused."
            if flag:
                break
        except Exception as e:
            print e
            user_input = raw_input("Connection broke, wanna retry? n to exit")
    print 'Console terminated.'

if __name__ == '__main__':
    main()
