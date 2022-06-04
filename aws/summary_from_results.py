import pandas as pd 
import numpy as np
import csv
import json
import sys,os
import pandas

for root, dirs, files in os.walk('result/'):
    array = dirs
    if array:
        D = array
        break

func = ['cs_bot', 'ep_users_sign_up', 'ep_products_table_update', 'ep_orders_create_order', 'ep_products_validate', 'ep_delivery_on_package_created', 
          'ep_payment_validate', 'ep_warehouse_on_order_events', 'ep_warehouse_table_update', 'ep_payment_cancel_payment', 'ep_delivery_table_requests', 'ep_payment_process_payment', 
          'ep_orders_on_event', 'ep_orders_table_update', 'ep_payment_update_payment', 'df_union', 'eo_athenarunner', 'eo_gluerunner', 'eo_ons3objectcreated', 'fmp_twitter_streaming', 
          'fmp_twitterddb', 'fmp_comparefaces', 'fp_notification', 'fp_conversion', 'fp_sentiment', 't_payment_method', 't_ddb_encrypt_item', 'sc_add_to_cart', 'sc_update_cart', 
          'sc_list_cart', 'sc_migrate_cart', 'sc_checkout_cart', 'sc_delete_from_cart', 'tcp_download_podcast', 'tcp_check_transcribe', 'tcp_process_podcast_rss', 'tcp_upload_to_elasticsearch', 'cer_lambda']

# generate cold_start.csv
def get(kind):
    res = {}
    for dir in D:
        res[dir] = {}
        filename = 'result/' + str(dir) + '/' + kind + '/result.csv'
        df = pd.read_csv(filename)
        for idx, row in df.iterrows():
            if float(row['time_from_system_start']) >= 1800 and row['container'] == 'create':
                action = row['action']
                if action not in res[dir]:
                    res[dir][action] = 0
                res[dir][action] += 1
    return res

openwhisk = get('openwhisk')
pagurus = get('pagurus')
prewarm = get('prewarm')
sock = get('sock')

rows = []
pagurus_total = {}
prewarm_total = {}
sock_total = {}
for action in func:
    pagurus_total[action] = []
    prewarm_total[action] = []
    sock_total[action] = []

for dir in D:
    for action in func:
        openwhisk_cold = openwhisk[dir][action] if action in openwhisk[dir] else 0
        pagurus_cold = pagurus[dir][action] if action in pagurus[dir] else 0
        prewarm_cold = prewarm[dir][action] if action in prewarm[dir] else 0
        sock_cold = sock[dir][action] if action in sock[dir] else 0
        pagurus_percent, random_percent, prewarm_percent, sock_percent = 0, 0, 0, 0
        if openwhisk_cold > 0:
            pagurus_percent = pagurus_cold / openwhisk_cold
            prewarm_percent = prewarm_cold / openwhisk_cold
            sock_percent = sock_cold / openwhisk_cold
        pagurus_total[action].append(pagurus_percent)
        prewarm_total[action].append(prewarm_percent)
        sock_total[action].append(sock_percent)
        
for action in func:
    pagurus_total[action] = np.mean(pagurus_total[action])
    prewarm_total[action] = np.mean(prewarm_total[action])
    sock_total[action] = np.mean(sock_total[action])

rows = []
for action in func:
    row = {'action': action, 'pagurus': pagurus_total[action],  'prewarm': prewarm_total[action], 'sock': sock_total[action]}
    rows.append(row)

file_name = 'result/cold_start.csv'
with open(file_name, mode='w') as csv_file:
    fieldnames = ['action', 'openwhisk', 'pagurus', 'prewarm', 'sock']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)



# generate startup_time.csv
def get(kind, way, key):
    res = {}
    for dir in D:
        filename ='result/' + str(dir) + '/' + kind + '/result.csv'
        df = pd.read_csv(filename)
        for idx, row in df.iterrows():
            if float(row['time_from_system_start']) >= 359 and row['container'] == way:
                action = row['action']
                if action not in res:
                    res[action] = []
                res[action].append(float(row[key]))
    return res

def div(a, b):
    if a == None or b == None:
        return None
    else:
        return a / b

openwhisk = get('openwhisk', 'create', 'create_time')
pagurus = get('pagurus', 'rent', 'rent_time')
prewarm = get('prewarm', 'prewarm', 'rent_time')
sock = get('sock', 'prewarm', 'rent_time')

rows = []
for action in func:
    openwhisk_mean = np.mean(openwhisk[action]) if action in openwhisk else None
    pagurus_mean = np.mean(pagurus[action]) if action in pagurus else None
    prewarm_mean = np.mean(prewarm[action]) if action in prewarm else None
    sock_mean = np.mean(sock[action]) if action in sock else None
    pagurus_ = div(pagurus_mean, openwhisk_mean)
    prewarm_ = div(prewarm_mean, openwhisk_mean)
    sock_ = div(sock_mean, openwhisk_mean)
    row = {'action': action, 'openwhisk': openwhisk_mean, 'pagurus': pagurus_mean, 'prewarm': prewarm_mean, 'sock': sock_mean, 'pagurus/openwhisk': pagurus_, 'prewarm/openwhisk': prewarm_, 'sock/openwhisk': sock_}
    rows.append(row)

file_name = 'result/startup_time.csv'
with open(file_name, mode='w') as csv_file:
    fieldnames = ['action', 'openwhisk', 'pagurus', 'prewarm', 'sock', 'pagurus/openwhisk', 'prewarm/openwhisk', 'sock/openwhisk']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)


# generate e2e_latency.csv
def get(kind, way):
    res = {}
    for dir in D:
        filename ='result/' + str(dir) + '/' + kind + '/result.csv'
        df = pd.read_csv(filename)
        for idx, row in df.iterrows():
            if float(row['time_from_system_start']) >= 359 and (row['container'] == way or row['container'] == 'create'):
                action = row['action']
                if action not in res:
                    res[action] = []
                res[action].append(float(row['end2end latency']))
    return res

openwhisk = get('openwhisk', 'create')
pagurus = get('pagurus', 'rent')
prewarm = get('prewarm', 'prewarm')
sock = get('sock', 'prewarm')

rows = []
for action in func:
    openwhisk_mean = np.mean(openwhisk[action]) if action in openwhisk else None
    pagurus_mean = np.mean(pagurus[action]) if action in pagurus else None
    prewarm_mean = np.mean(prewarm[action]) if action in prewarm else None
    sock_mean = np.mean(sock[action]) if action in sock else None
    pagurus_ = div(pagurus_mean, openwhisk_mean)
    prewarm_ = div(prewarm_mean, openwhisk_mean)
    sock_ = div(sock_mean, openwhisk_mean)
    row = {'action': action, 'openwhisk': openwhisk_mean, 'pagurus': pagurus_mean, 'prewarm': prewarm_mean, 'sock': sock_mean, 'pagurus/openwhisk': pagurus_, 'prewarm/openwhisk': prewarm_, 'sock/openwhisk': sock_}
    rows.append(row)

file_name = 'result/e2e_latency.csv'
with open(file_name, mode='w') as csv_file:
    fieldnames = ['action', 'openwhisk', 'pagurus', 'prewarm', 'sock', 'pagurus/openwhisk', 'prewarm/openwhisk', 'sock/openwhisk']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
