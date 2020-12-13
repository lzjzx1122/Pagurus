import requests

url = 'http://0.0.0.0:5001/linpack/run'
request_id = 'test1'
params = {'param': 100}
res = requests.post(url, json = {'request_id': str(request_id), 'data': params})
