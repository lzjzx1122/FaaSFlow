import json
import socket
import time

s = socket.socket()
s.bind(('0.0.0.0', 5999))
s.listen(100)

while True:
    c, addr = s.accept()
    client_data = c.recv(64 * 1024)
    # time.sleep(0.005)
    data = json.loads(client_data)
    print(data)
    c.close()
