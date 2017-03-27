# -*- coding: utf-8 -*-
# @Time  : 2017/3/26 16:13
# @Author: FSOL
# @File  : fabfile.py

"""
Thanks for my senior xjlin's fab file! I made a little change.
"""
# __author__ = 'xjlin'
# -*- coding: utf-8 -*-

from fabric.api import *

# All servers
King = {
    'name': 'ip'
}
Soldier = {
    'name': 'ip'
}

PATH = '/home/ubuntu/New_web'
PROJECT = 'New_web'


def set_host(name='all'):
    env.hosts = []
    if name == 'soldier':
        for _, host in Soldier.iteritems():
            env.hosts.append('ubuntu@{}'.format(host))
    elif name == 'all':
        for _, host in King.iteritems():
            env.hosts.append('ubuntu@{}'.format(host))
        for _, host in Soldier.iteritems():
            env.hosts.append('ubuntu@{}'.format(host))
    elif name == 'king':
        for _, host in King.iteritems():
            env.hosts.append('ubuntu@{}'.format(host))
    elif name in King:
        host = King[name]
        env.hosts = ['ubuntu@{}'.format(host)]
    else:
        host = Soldier[name]
        env.hosts = ['ubuntu@{}'.format(host)]


def deploy(project=PROJECT):
    with settings(warn_only=True):
        if run("test -d {}".format(project)).failed:
            run('git clone git@github.com:sinnfashen/New_web.git')
        else:
            with cd(PATH):
                run('git pull')


def remove(project=PROJECT):
    with settings(warn_only=True):
        if run("Test -d {}".format(project)).failed:
            pass
        else:
            run('rm -rf /home/ubuntu/{}'.format(project))


def king_start():
    sh_folder = '/'.join((PATH, 'Tools', 'fabs'))
    with settings(warn_only=True):
        with cd(sh_folder):
            run('screen -d -m bash king_start.sh', pty=False)


def soldier_start():
    sh_folder = '/'.join((PATH, 'Tools', 'fabs'))
    with settings(warn_only=True):
        with cd(sh_folder):
            run('screen -d -m bash soldier_start.sh', pty=False)


def install_config(project=PROJECT):
    with settings(warn_only=True):
        put('/PATH/TO/CONFIG', '/home/ubuntu/New_web/config.py')


def kill():
    sh_folder = '/'.join((PATH, 'Tools', 'fabs'))
    with settings(warn_only=True):
        with cd(sh_folder):
            run('./kill.sh')


def add_key():
    with open('id_rsa.pub') as f:
        line = f.readlines()[0:1][0].strip('\n')
    with settings(warn_only=True):
        run('echo {} >> .ssh/authorized_keys'.format(line))
