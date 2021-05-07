import json

f = open('aws_packages.json', 'r', encoding='utf-8')
data = json.load(f)
print(data.keys())
