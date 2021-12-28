import sys
import requests

base_url = 'http://127.0.0.1:{}/{}'

data = {'action': sys.argv[1]}
r = requests.post(base_url.format(15000, 'init'), json=data)
print(r)
