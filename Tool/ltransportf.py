
def savesend(buffer,target):
    try:
        target.send('{};{}'.format(len(buffer), SENTBUFFER))
        if target.recv(1024) == 'Ready':
            target.sendall(buffer)
            return "Send Success"
    except Exception as e:
        return "Send rejected:{}".format(e)


def saverecv(target):
    try:
        BUFFER = target.recv(1024)
        target.send("Ready")
        BUFFER = target.recv(BUFFER.split(ORDER)[1]+10)
        return "Recv Success"
    except Exception as e:
        return "Recv error:{}".format(e)