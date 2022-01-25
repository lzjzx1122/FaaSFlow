import requests

r = requests.post('http://localhost:7000/run', json={'workflow': 'soykb', 'request_id': 'abcde'})
print(r.text)