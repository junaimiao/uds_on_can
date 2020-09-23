import sys
import redis
import pickle

# cache = redis.StrictRedis("127.0.0.1",6379)
# cache.set("my_name","hzc")

# print(cache.ping())
# print(cache.get("my_name"))
# cache.delete("my_name")

r = redis.StrictRedis("127.0.0.1",6379)

if r.get("line_number") != None:
    print("存在")
else:
    print("不存在")

print(r.get("line_number"))