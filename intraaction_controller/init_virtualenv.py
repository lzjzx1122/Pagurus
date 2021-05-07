import os
import json


init_file = open('init_virtualenv.bash', 'w', encoding='utf-8')
virtualenv_path = './virtualenv/'
for cur_path, cur_dirs, cur_files in os.walk('./init_virtualenv_config'):
    for file_name in cur_files:
        cur_file_path = cur_path + '/' + file_name
        print('----Current Files: ' + cur_file_path + '----')
        config_file = open(cur_file_path, 'r', encoding='utf-8') 
        data = json.load(config_file)
        config_file.close()
        for function_name in data['functions']:
            function_data = data['functions'][function_name]
            print('----Building virtualenv for function: ' + function_name + '----')
            init_file.write('virtualenv -p /usr/bin/python3 ' + virtualenv_path + function_name + '\n')
            print('----Activating env----')
            init_file.write('source ' + virtualenv_path + function_name + '/bin/activate\n')
            print('----Installing----')
            for package in function_data['packages']:
                version = function_data['packages'][package]['version']
                init_file.write('pip3 install ' + package + '==' + version + '\n')
            print('----Deactivating----')
            init_file.write('deactivate\n')
init_file.close()