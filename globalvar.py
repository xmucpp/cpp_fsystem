import redis
import time
import os
import socket
import select

# ------epoll
epoll = select.epoll()
# ------timeout
timeout = 20
socket.setdefaulttimeout(timeout)
# ------redis
RedisServer = '123.207.93.47'
redis = redis.Redis(RedisServer)
# ------self
HOST = ''
PORT = 9813
# ------serverinfo---------
serverlist = {}
console = {}
unidentified = {}
worker = {}
workerstate = {}
worktable = {'TMALL': ''}
crawlerstatis = {'TMALL': 0,'FAKE': 0}
missionglist = {'TMALL': 0, 'FAKE': 0}
# -------constant
OUTTIME = 300
BUFFER = ''
SENTBUFFER = 1024
# -------code
CONNECTPASSWORD = '53454283b08400215b300d0ba0f67cdc'
CONNECTCOMFIRM = 'COMFIRM'
CONSOLEPASSWORD = '4b313d3d672bb419d01dbd6572976709'
CONNECTSUCCESS = 'Connection established'
BACKUP = 'B-'
ORDER = ';'
IPPORT = '#'
# -------tigger
order_to_close = False
order_to_update = False
# -------time
PRESENT_DAY = str(time.strftime('%Y-%m-%d', time.localtime(time.time())))

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 Safari/537.36 SE 2.X MetaSr 1.0'

    'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
    'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
    'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11',
    'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',

    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler 4.0)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; The World)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Avant Browser)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',

]

PATH = os.path.abspath(os.path.dirname(__file__))
ROOTPATH = '/home/ubuntu'