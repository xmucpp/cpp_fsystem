# -*- coding: utf-8 -*-
# @Time  : 2017/3/27 22:44
# @Author: FSOL
# @File  : md5.py

import hashlib

def encry(password):
    return hashlib.md5(password).hexdigest()

if __name__ == "__main__":
    x = raw_input()
    print(encry(x))
