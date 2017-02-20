import redis
re = redis.Redis()
for i in range(1,1000,1):
    re.lpush('FAKE', i)