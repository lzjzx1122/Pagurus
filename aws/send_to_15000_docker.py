import sys
import requests

base_url = 'http://127.0.0.1:{}/{}'

data = {'action': sys.argv[2]}
r = requests.post(base_url.format(sys.argv[1], 'init'), json=data)
print(r)
