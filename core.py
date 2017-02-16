import socket
import commands
import select
import time
import json
from code import *

HOST = ''
PORT = 9813
serverlist = {}
console = {}
unidentified = {}

OUTTIME = 300
BUFFER = ''


def system(order):
    if len(order) > 2:
        return "wrong arguments number\n"

    status, results = commands.getstatusoutput(order[1])
    if status == 0 and results != '':
        return results
    elif status == 0 and results == '':
        return "Success!\n"
    else:
        return 'ERROR:{}\n{}\n'.format(status, results)


def connect(order):
    if len(order) != 3:
        return "wrong arguments number"

    try:
        order[2] = int(order[2])
    except Exception as e:
        return "port Error!"

    so = socket.socket()

    try:
        so.connect((order[1], order[2]))
    except Exception as e:
        return 'IP Error!\n{}'.format(e)
    so.send(CONNECTPASSWORD)
    BUFFER = so.recv(1024)
    if BUFFER == CONNECTCOMFIRM:
        serverlist[so.fileno()] = so
        return CONNECTSUCCESS
    else:
        return BUFFER


def info(order):
    infodata = 'Connected Server:{}\n'.format(len(serverlist))
    for (fileno, server) in serverlist.items():
        peername = server.getpeername()
        infodata += "%-4d      %-12s     %-5d     \n" % (fileno, peername[0], peername[1])
    infodata += '\n\n\nConnected Console:{}\n'.format(len(console))
    for (fileno, con) in console.items():
        peername = con.getpeername()
        infodata += "%-4d      %-12s     %-5d     \n" % (fileno, peername[0], peername[1])
    infodata += '\n\n\nUnidentified Request:{}\n'.format(len(unidentified))
    for (fileno, uni) in unidentified.items():
        peername = uni[1].getpeername()
        infodata += "%-4d      %-12s     %-5d     %-5.0f\n" % (fileno, peername[0], peername[1], time.time()-uni[0])
    return infodata


server_operation = {'SYSTEM': system, 'CONNECT': connect, 'INFO': info}


def serverorder(message):
    if message.find(ORDER) == -1:
        order = [message]
    else:
        order = message.split(ORDER)
    return server_operation[order[0]](order)


'''-----------------------------------------'''
Collective = lambda x: x
Allin = lambda x: x.insert(1, 'ALL')
Local = lambda x: x.insert(1, '-1')

operation = {
    'SYSTEM': Collective,
    'CONNECT': Allin,
    'INFO': Local,
}


def collective(order):
    try:
        if order[1] != 'ALL':
            targetlist = json.loads('[{}]'.format(order[1]))
        else:
            targetlist = serverlist.keys()
            targetlist.append(-1)
    except Exception as e:
        return "----ERROR!!!----\nTargetlist Error\n{}".format(e)

    order.pop(1)
    orderm = ';'.join([str(e) for e in order])
    print order,orderm,targetlist
    results = ''
    for target in targetlist:
        if target == -1:
            results += '{}:  {}\n'.format(target, serverorder(orderm))
        else:
            serverlist[target].send(orderm)
            results += '{}:  {}\n'.format(target, serverlist[target].recv(1024))

    return results


def consoleorder(message):
    if message.find(ORDER) == -1:
        order = [message]
    else:
        order = message.split(ORDER)
    if order[0] not in operation:
        return "no such service"
    else:
        operation[order[0]](order)
        return collective(order)


'''-----------------------------------------'''


def main():
    self = socket.socket()
    self.bind((HOST, PORT))
    self.listen(10)

    epoll = select.epoll()
    epoll.register(self.fileno(), select.EPOLLIN)
    print "--------------------------------\n       SYSTEM STARTED"
    while True:
        events = epoll.poll(5)
        for fileno , event in events:

            if fileno == self.fileno():
                con,conaddr = self.accept()
                print conaddr, "in coming connection"
                epoll.register(con.fileno(), select.EPOLLIN)
                unidentified[con.fileno()] = [time.time(), con]

            elif fileno in unidentified:
                BUFFER = unidentified[fileno][1].recv(1024)
                print fileno, " message:", BUFFER
                if BUFFER == CONNECTPASSWORD:
                    serverlist[fileno] = unidentified[fileno][1]
                    unidentified.pop(fileno)
                    serverlist[fileno].send(CONNECTCOMFIRM)
                    print '{}: {}----server connected'.format(fileno, serverlist[fileno].getpeername())
                elif BUFFER == CONSOLEPASSWORD:
                    console[fileno] = unidentified[fileno][1]
                    unidentified.pop(fileno)
                    console[fileno].send(CONNECTCOMFIRM)
                    print '{}: {}----console connected'.format(fileno, console[fileno].getpeername())
                elif BUFFER == '':
                    print '{}: {}----unidentified disconnected'.format(fileno, unidentified[fileno][1].getpeername())
                    epoll.modify(fileno, 0)
                    unidentified.pop(fileno)
                else:
                    unidentified[fileno][1].send("WRONG PASSWORD!")
                    print '{}: {}----unidentified tried a wrong password'.format(fileno, unidentified[fileno][1].getpeername())

            elif fileno in console:
                BUFFER = console[fileno].recv(1024)
                print "message from console{}:\n{}".format(fileno, BUFFER)
                if BUFFER == '':
                    epoll.modify(fileno, 0)
                    console.pop(fileno)
                else:
                    console[fileno].sendall(consoleorder(BUFFER))

            elif fileno in serverlist:
                BUFFER = serverlist[fileno].recv(1024)
                print "message from server{}:\n{}".format(fileno, BUFFER)
                if BUFFER == '':
                    epoll.modify(fileno, 0)
                    serverlist.pop(fileno)
                else:
                    serverlist[fileno].sendall(serverorder(BUFFER))

            else:
                print "what?"

        for (fileno, uni) in unidentified.items():
            if time.time() - uni[0] >= OUTTIME:
                cli = uni[1]
                cli.send("auto disconnect\n")
                unidentified.pop(cli.fileno())
                cli.close()


if __name__ == "__main__":
    main()
