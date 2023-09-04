import hashlib

with open('test.mp4', 'rb') as f:
    data = f.read()
md5 = hashlib.md5()
md5.update(data)
print(md5.hexdigest())