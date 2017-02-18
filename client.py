import socket
import readline


def communicate(server):
    user_input = ''
    while user_input != 'exit':
        usrinput = raw_input('-->')
        server.send(usrinput)
        message = server.recv(1024)
        if message == '':
            break
        print message
    server.close()


def main():
    print "---------------------------\n      Initializing....\n"
    while True:
        server = socket.socket()
        server.connect(('127.0.0.1', 9813))
        user_input = raw_input("Please input the password to server(exit to close):")
        server.send(user_input)
        if user_input == 'exit':
            break
        message = server.recv(1024)
        if message == 'COMFIRM':
            print "Connection established."
            communicate(server)
            print "Disconnected."
        else:
            print "Connection refused."
    print 'Console terminated.'

if __name__ == '__main__':
    main()
