import redis
import json

r = redis.StrictRedis(host='172.17.0.1', port=6380, db=0)
for key in r.keys():
    print(key)
