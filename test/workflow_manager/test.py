import requests

url = 'http://localhost:7000/run'
data = {'workflow': 'wordcount', 'request_id': '1'}
requests.post(url, json=data)