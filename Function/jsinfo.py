# -*- coding: utf-8 -*-
# @Time  : 2017/3/25 16:04
# @Author: FSOL
# @File  : jsinfo.py

import json

import Work.globalvar as gv
from Work.log import Logger
logger = Logger('Function', 'DEBUG')

def jsinfo(order):
    info_data = json.dumps({'sl': len(gv.serverlist),
                 'cl': len(gv.console),
                 'ul': len(gv.unidentified),
                 'wk': {work: {'s': gv.worker[work].state,
                         't': gv.worker[work].table, 'c': gv.crawlerstatis[work]} for work in gv.worker.keys()},
                 'ms': {mission: {'s': gv.mission_list[mission].state,
                         'h': gv.mission_list[mission].hour, 'm': gv.mission_list[mission].minute}
                        for mission in gv.mission_list.keys()}
                           })
    return info_data


def collect(message, target_list):
    results = {'sl': len(gv.serverlist),
               'cl': len(gv.console),
               'ul': len(gv.unidentified),
               'wk': {cf.RedisServer: {work: {'s': gv.worker[work].state,
                     't': gv.worker[work].table} for work in gv.worker.keys()}},
               'st': {work: gv.crawlerstatis[work] for work in gv.worker.keys()},
               'ms': {mission: {'s': gv.mission_list[mission].state,
                     'h': gv.mission_list[mission].hour, 'm': gv.mission_list[mission].minute}
                      for mission in gv.mission_list.keys()},
               'Wsl': {}, 'Wms': {}
               }
    for target in target_list:
        try:
            if target == -1:
                pass
            else:
                gv.serverlist[target].send(message)
                temp = json.loads(gv.serverlist[target].recv(1024))
                if temp['sl'] != results['sl']:
                    results['Wsl'][gv.serverlist[target].getpeername()[0]] = temp['sl']
                results['cl'] += temp['cl']
                results['ul'] += temp['ul']
                results['wk'][gv.serverlist[target].getpeername()[0]] = {}
                for work in temp['wk']:
                    results['wk'][gv.serverlist[target].getpeername()[0]][work] = \
                        {'s': temp['wk'][work]['s'], 't': temp['wk'][work]['t']}
                    results['st'][work] += temp['wk'][work]['c']
                results['Wms'][gv.serverlist[target].getpeername()[0]] = {}
                for mission in temp['ms']:
                    if results['ms'][mission] != temp['ms'][mission]:
                        results['Wms'][gv.serverlist[target].getpeername()[0]][mission] = temp['ms'][mission]
        except Exception:
            logger.error(logger.traceback())
    return json.dumps(results)

functions = {
    'jsinfo': {'entry': jsinfo, 'argu_num': 0, 'dis_mode': 0,
               'way_to_use': 'jsinfo',
               'help_info': 'Return state account in json.',
               'collect': collect}
}