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
            results += '-----------------------------------\n'
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
    'UPDATE': Collective,
    'CANCEL': Collective,
    'MISSION': Collective,
    'HELP': 0
}

help_list = '--------Caution: All servers are specified by its fileno\n' \
            '--------Lowercase part needs to be replaced.\n' \
            'SYSTEM;server;order                        ----Execute System(linux) order on specified server\n' \
            'CONNECT;ip;port;password                   ----Connect to specified new server\n' \
            'INFO;server                                ----Obtain detailed information of specified server\n' \
            'STATISTICS                                 ----Obtain briefings of all servers\n' \
            'CRAWLER;server;crawlername                 ----Start selected Crawler on specified server\n' \
            'SHUTDOWN;server                            ----Shutdown specified server\n' \
            'UPDATE;server                              ----Self-update from git\n' \
            'MISSION;server;crawler;order;hour;min      ----Time crawler to automatically run at hour:min every day\n' \
            'CANCEL;server;crawler                      ----Cancel a running crawler\n' \
            'HELP                                       ----Ask for the current page\n'


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
