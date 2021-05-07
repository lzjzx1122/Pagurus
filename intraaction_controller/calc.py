import json
import pandas as pd


rows = []
func_pack = json.load(open('./build_file/packages.json', 'r'))
for function in func_pack:
    size = 0
    for package in func_pack[function]:
        size = size + func_pack[function][package]
    rows.append({'function': function, 'package_size': size})
result = pd.DataFrame.from_records(rows)
result.to_csv('./package_size.csv', index=False)
