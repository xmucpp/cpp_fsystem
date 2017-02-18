# git clone https://github.com/sinnfashen/New_web
import socket
import select
import time
import commands

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


def main():

    self = socket.socket()
    self.bind((gv.HOST, gv.PORT))
    self.listen(10)

    epoll = select.epoll()
    epoll.register(self.fileno(), select.EPOLLIN)
    print "--------------------------------\n       SYSTEM STARTED"

    while True:
        if gv.order_to_close:
            break
        if gv.order_to_update:
            reloading()

        events = epoll.poll(20)
        print events
        for fileno, event in events:
            if fileno == self.fileno():
                con, conaddr = self.accept()
                print conaddr, "Incoming Connection"
                epoll.register(con.fileno(), select.EPOLLIN)
                gv.unidentified[con.fileno()] = [time.time(), con]

            elif fileno in gv.unidentified:
                gv.BUFFER = gv.unidentified[fileno][1].recv(1024)
                if gv.BUFFER == gv.CONNECTPASSWORD:
                    gv.serverlist[fileno] = gv.unidentified[fileno][1]
                    gv.unidentified.pop(fileno)
                    gv.serverlist[fileno].send(gv.CONNECTCOMFIRM)
                    print '{}: {}----server connected'.format(fileno, gv.serverlist[fileno].getpeername())
                elif gv.BUFFER == gv.CONSOLEPASSWORD:
                    gv.console[fileno] = gv.unidentified[fileno][1]
                    gv.unidentified.pop(fileno)
                    gv.console[fileno].send(gv.CONNECTCOMFIRM)
                    print '{}: {}----console connected'.format(fileno, gv.console[fileno].getpeername())
                elif gv.BUFFER == '':
                    print '{}: {}----unidentified disconnected'.format(fileno, gv.unidentified[fileno][1].getpeername())
                    epoll.modify(fileno, 0)
                    gv.unidentified.pop(fileno)
                else:
                    gv.unidentified[fileno][1].send("WRONG PASSWORD!")
                    print '{}: {}----unidentified tried a wrong password'\
                        .format(fileno, gv.unidentified[fileno][1].getpeername())

            elif fileno in gv.console:
                gv.BUFFER = gv.console[fileno].recv(1024)
                print "message from console {}:\n{}".format(fileno, gv.BUFFER)
                if gv.BUFFER == '':
                    epoll.modify(fileno, 0)
                    gv.console.pop(fileno)
                else:
                    gv.console[fileno].sendall(consoleops.console_order(gv.BUFFER))

            elif fileno in gv.serverlist:
                gv.BUFFER = gv.serverlist[fileno].recv(1024)
                print "message from server{}:\n{}".format(fileno, gv.BUFFER)
                if gv.BUFFER == '':
                    epoll.modify(fileno, 0)
                    gv.serverlist.pop(fileno)
                else:
                    gv.serverlist[fileno].sendall(serverops.server_order(gv.BUFFER))

            else:
                print "what?"

        for (fileno, uni) in gv.unidentified.items():
            if time.time() - uni[0] >= gv.OUTTIME:
                cli = uni[1]
                cli.send("auto disconnect\n")
                gv.unidentified.pop(cli.fileno())
                cli.close()

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
