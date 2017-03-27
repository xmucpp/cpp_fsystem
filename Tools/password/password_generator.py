# -*- coding: utf-8 -*-
# @Time  : 2017/3/27 22:44
# @Author: FSOL
# @File  : password_generator.py

import random
charset = list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*")
length = 32
password = []
for i in range(0, length, 1):
    password.append(random.choice(charset))
print(''.join(password))
