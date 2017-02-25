# -*- coding: utf-8 -*-
# @Author: FSOL
# @File  : client.py

import socket
import readline
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
    server.close()
    if user_input == 'exit':
        return 1
    return 0


def main():
    print "---------------------------\n      Initializing....\n"
    user_input = ''
    while user_input != 'n':
        server = socket.socket()
        try:
            server.connect(('127.0.0.1', 9813))
            user_input = raw_input("Please input the password to server(exit to close):")
            server.send(user_input)
            if user_input == 'exit':
                break
            message = server.recv(8192)
            if message == 'COMFIRM':
                print "Connection established."
                if communicate(server):
                    break
                print "Disconnected."
            else:
                print "Connection refused."
        except Exception as e:
            print e
            user_input = raw_input("Wanna retry? n to exit")
    print 'Console terminated.'

if __name__ == '__main__':
    main()
