import time


def parse(url):
    print 'worker:{}'.format(url)
    time.sleep(1)
    return 0