import json

d = {}
for i in range(388):
    d['utility' + str(i)] = {}

f = open('azure_packages.json', 'w', encoding='utf-8')
json.dump(d, f, sort_keys = False)
