# -*- coding: utf-8 -*-
# @Author: FSOL
# @File  : testdata.py

import redis
re = redis.Redis()
for i in range(1,1000,1):
    re.lpush('FAKE', i)