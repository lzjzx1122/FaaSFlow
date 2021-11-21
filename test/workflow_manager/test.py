import requests

url = 'http://localhost:7000/run'
data = {'workflow': 'epigenomics', 'request_id': '1'}
requests.post(url, json=data)