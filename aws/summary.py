import pandas as pd 
import numpy as np
import csv
import json
import sys
import pandas

dir = sys.argv[1]

func = ['cs_bot', 'ep_users_sign_up', 'ep_products_table_update', 'ep_orders_create_order', 'ep_products_validate', 'ep_delivery_on_package_created', 
          'ep_payment_validate', 'ep_warehouse_on_order_events', 'ep_warehouse_table_update', 'ep_payment_cancel_payment', 'ep_delivery_table_requests', 'ep_payment_process_payment', 
          'ep_orders_on_event', 'ep_orders_table_update', 'ep_payment_update_payment', 'df_union', 'eo_athenarunner', 'eo_gluerunner', 'eo_ons3objectcreated', 'fmp_twitter_streaming', 
          'fmp_twitterddb', 'fmp_comparefaces', 'fp_notification', 'fp_conversion', 'fp_sentiment', 't_payment_method', 't_ddb_encrypt_item', 'sc_add_to_cart', 'sc_update_cart', 
          'sc_list_cart', 'sc_migrate_cart', 'sc_checkout_cart', 'sc_delete_from_cart', 'tcp_download_podcast', 'tcp_check_transcribe', 'tcp_process_podcast_rss', 'tcp_upload_to_elasticsearch', 'cer_lambda']

# generate cold_start.csv
def get(filename):
    df = pd.read_csv(filename)
    res = {}
    for idx, row in df.iterrows():
        if float(row['time_from_system_start']) >= 1800 and row['container'] == 'create':
            action = row['action']
            if action not in res:
                res[action] = 0
            res[action] += 1
    return res

openwhisk = get(dir + '/openwhisk/result.csv')
pagurus = get(dir + '/pagurus/result.csv')
prewarm = get(dir + '/prewarm/result.csv')
sock = get(dir + '/sock/result.csv')

openwhisk_total, pagurus_total, prewarm_total, sock_total = 0, 0, 0, 0
rows = []
for action in func:
    openwhisk_cold = openwhisk[action] if action in openwhisk else 0
    pagurus_cold = pagurus[action] if action in pagurus else 0
    prewarm_cold = prewarm[action] if action in prewarm else 0
    sock_cold = sock[action] if action in sock else 0
    openwhisk_total += openwhisk_cold
    pagurus_total += pagurus_cold
    prewarm_total += prewarm_cold
    sock_total += sock_cold
row = {'action': 'all', 'openwhisk': openwhisk_total, 'pagurus': pagurus_total, 'prewarm': prewarm_total, 'sock': sock_total}
rows.append(row)

for action in func:
    openwhisk_cold = openwhisk[action] if action in openwhisk else 0
    pagurus_cold = pagurus[action] if action in pagurus else 0
    prewarm_cold = prewarm[action] if action in prewarm else 0
    sock_cold = sock[action] if action in sock else 0
    row = {'action': action, 'openwhisk': openwhisk_cold, 'pagurus': pagurus_cold, 'prewarm': prewarm_cold, 'sock': sock_cold}
    rows.append(row)

file_name = dir + '/cold_start.csv'
with open(file_name, mode='w') as csv_file:
    fieldnames = ['action', 'openwhisk', 'pagurus', 'prewarm', 'sock']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)

# generate startup_time.csv
def get(filename, way, key):
    df = pd.read_csv(filename)
    res = {}
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

openwhisk = get(dir + '/openwhisk/result.csv', 'create', 'create_time')
pagurus = get(dir + '/pagurus/result.csv', 'rent', 'rent_time')
prewarm = get(dir + '/prewarm/result.csv', 'prewarm', 'rent_time')
sock = get(dir + '/sock/result.csv', 'prewarm', 'rent_time')

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

file_name = dir + '/startup_time.csv'
with open(file_name, mode='w') as csv_file:
    fieldnames = ['action', 'openwhisk', 'pagurus', 'prewarm', 'sock', 'pagurus/openwhisk', 'prewarm/openwhisk', 'sock/openwhisk']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)


# generate e2e_latency.csv
def get(filename, way):
    df = pd.read_csv(filename)
    res = {}
    for idx, row in df.iterrows():
        if float(row['time_from_system_start']) >= 359 and (row['container'] == way or row['container'] == 'create'):
            action = row['action']
            if action not in res:
                res[action] = []
            res[action].append(float(row['end2end latency']))
    return res

openwhisk = get(dir + '/openwhisk/result.csv', 'create')
pagurus = get(dir + '/pagurus/result.csv', 'rent')
prewarm = get(dir + '/prewarm/result.csv', 'prewarm')
sock = get(dir + '/sock/result.csv', 'prewarm')

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

file_name = dir + '/e2e_latency.csv'
with open(file_name, mode='w') as csv_file:
    fieldnames = ['action', 'openwhisk', 'pagurus', 'prewarm', 'sock', 'pagurus/openwhisk', 'prewarm/openwhisk', 'sock/openwhisk']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)