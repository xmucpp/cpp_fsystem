import globalvar as gv
import json
import serverops

def reloading():
    pass


def collective(order):
    try:
        if order[1].upper() != 'ALL':
            target_list = json.loads('[{}]'.format(order[1]))
        else:
            target_list = gv.serverlist.keys()
            target_list.append(-1)
    except Exception as e:
        return "----ERROR!!!----\n" \
               "Target server list Error\n" \
               "Use 'ALL'(no case insensitive) or 1,3,4(fileno of server)\n" \
               "{}".format(e)

    order.pop(1)
    message = ';'.join([str(e) for e in order])
    results = ''
    for target in target_list:
        try:
            if target == -1:
                results += 'local(-1):  {}\n'.format(serverops.server_order(message))
            else:
                gv.serverlist[target].send(message)
                results += '{}:  {}\n'.format(target, gv.serverlist[target].recv(1024))
        except Exception as e:
            results += '{}:Error!  {}\n'.format(target, e)

    return results

Collective = lambda x: x
Allin = lambda x: x.insert(1, 'ALL')
Local = lambda x: x.insert(1, '-1')

operation = {
    'SYSTEM': Collective,
    'CONNECT': Allin,
    'INFO': Collective,
    'STATISTICS': Allin,
    'CRAWLER': Collective,
    'SHUTDOWN': Collective,
    'HELP': 0
}

help_list = '--------Caution: ALL server are standed by its fileno\n' \
            'SYSTEM;server;order                ----System order\n' \
            'CONNECT;IP;PORT                    ----Connect new server\n' \
            'INFO;server                        ----Detail information of server\n' \
            'STATISTICS                         ----Pandect of all servers\n' \
            'CRAWLER;server;crawlername         ----Start some Crawler on server\n' \
            'SHUTDOWN;server                    ----Shutdown server\n' \
            'HELP                               ----Ask for this page\n'


def console_order(message):
    if message.find(gv.ORDER) == -1:
        order = [message]
    else:
        order = message.split(gv.ORDER)
    if order[0].upper() not in operation:
        return "No such service\n" \
               "Do you need 'HELP'?"
    elif order[0].upper() == 'HELP':
        return help_list
    else:
        order[0] = order[0].upper()
        operation[order[0]](order)
        return collective(order)
