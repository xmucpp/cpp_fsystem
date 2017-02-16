import socket
import readline
print "---------------------------\n      Initializing...."
server = socket.socket()
server.connect(('127.0.0.1', 9813))
usrinput = ''
server.send('ppYOE%#u5yHpzi#H')
BUFFER = server.recv(1024)
if(BUFFER == 'COMFIRM'):
    print "Connection established"
    while usrinput != 'exit':
        usrinput = raw_input('-->')
        server.send(usrinput)
        BUFFER = server.recv(1024)
        print BUFFER
else:
    print "Connection refused"
print 'console terminated.'