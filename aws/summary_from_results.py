import pandas as pd 
import numpy as np
import csv
import json
import threading

D = [2, 3, 4, 5, 6, 7, 8, 9, 10, 13, 14, 15, 17, 18, 19, 20, 21, 22]

func = ['cs_bot', 'ep_users_sign_up', 'ep_products_table_update', 'ep_orders_create_order', 'ep_products_validate', 'ep_delivery_on_package_created', 
          'ep_payment_validate', 'ep_warehouse_on_order_events', 'ep_warehouse_table_update', 'ep_payment_cancel_payment', 'ep_delivery_table_requests', 'ep_payment_process_payment', 
          'ep_orders_on_event', 'ep_orders_table_update', 'ep_payment_update_payment', 'df_union', 'eo_athenarunner', 'eo_gluerunner', 'eo_ons3objectcreated', 'fmp_twitter_streaming', 
          'fmp_twitterddb', 'fmp_comparefaces', 'fp_notification', 'fp_conversion', 'fp_sentiment', 't_payment_method', 't_ddb_encrypt_item', 'sc_add_to_cart', 'sc_update_cart', 
          'sc_list_cart', 'sc_migrate_cart', 'sc_checkout_cart', 'sc_delete_from_cart', 'tcp_download_podcast', 'tcp_check_transcribe', 'tcp_process_podcast_rss', 'tcp_upload_to_elasticsearch', 'cer_lambda']


def get(kind, res):
    for dir in D:
        filename = str(dir) + '_' + kind + '/cold_results.csv'
        print(filename)
        df = pd.read_csv(filename)
        res[dir] = {}
        for idx, row in df.iterrows():
            if float(row['relative']) >= 1800:
                action = row['action']
                if action not in res[dir]:
                    res[dir][action] = {'total': 0, 'cold': 0}
                res[dir][action]['total'] += 1
                if row['container_way'] == 'create':
                    res[dir][action]['cold'] += 1
    return res

'''
openwhisk = get('openwhisk')
pagurus = get('pagurus')
prewarm = get('prewarm_no_ossystem')
random = get('random')
sock = get('sock_no_ossystem')
'''
openwhisk = {}
pagurus = {}
prewarm = {}
random = {}
sock = {}
t1 = threading.Thread(target=get, args=('openwhisk', openwhisk))
t2 = threading.Thread(target=get, args=('pagurus', pagurus))
t3 = threading.Thread(target=get, args=('prewarm_no_ossystem', prewarm))
t4 = threading.Thread(target=get, args=('random', random))
t5 = threading.Thread(target=get, args=('sock_no_ossystem', sock))
t1.start()
t2.start()
t3.start()
t4.start()
t5.start()
t1.join()
t2.join()
t3.join()
t4.join()
t5.join()

rows = []
pagurus_total = {}
random_total = {}
prewarm_total = {}
sock_total = {}
for action in func:
    pagurus_total[action] = []
    random_total[action] = []
    prewarm_total[action] = []
    sock_total[action] = []

for dir in D:
    for action in func:
        openwhisk_cold = openwhisk[dir][action]['cold'] if action in openwhisk[dir] else 0
        pagurus_cold = pagurus[dir][action]['cold'] if action in pagurus[dir] else 0
        random_cold = random[dir][action]['cold'] if action in random[dir] else 0
        prewarm_cold = prewarm[dir][action]['cold'] if action in prewarm[dir] else 0
        sock_cold = sock[dir][action]['cold'] if action in sock[dir] else 0
        pagurus_percent, random_percent, prewarm_percent, sock_percent = 0, 0, 0, 0
        if openwhisk_cold > 0:
            pagurus_percent = pagurus_cold / openwhisk_cold
            random_percent = random_cold / openwhisk_cold
            prewarm_percent = prewarm_cold / openwhisk_cold
            sock_percent = sock_cold / openwhisk_cold
        pagurus_total[action].append(pagurus_percent)
        random_total[action].append(random_percent)
        prewarm_total[action].append(prewarm_percent)
        sock_total[action].append(sock_percent)
        
for action in func:
    pagurus_total[action] = np.mean(pagurus_total[action])
    random_total[action] = np.mean(random_total[action])
    prewarm_total[action] = np.mean(prewarm_total[action])
    sock_total[action] = np.mean(sock_total[action])

rows = []
for action in func:
    row = {'action': action, 'pagurus': pagurus_total[action], 'random': random_total[action], 'prewarm': prewarm_total[action], 'sock': sock_total[action]}
    rows.append(row)

file_name = 'cold_percent.csv'
with open(file_name, mode='w') as csv_file:
    fieldnames = ['action', 'pagurus', 'random', 'prewarm', 'sock']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)

       
      
         
def get2(kind, way, v):
    res = {}
    for dir in D:
        filename = str(dir) + '_' + kind + '/cold_results.csv'
        print(filename)
        df = pd.read_csv(filename)
        start = float(df['inter_start'][0])
        for idx, row in df.iterrows():
            if float(row['inter_start']) - start >= 359:
                action = row['action']
                if action not in res:
                    res[action] = []
                if row['container_way'] == way:
                    res[action].append(float(row[v]))
    return res

openwhisk = get2('openwhisk', 'create', 'create_time')
pagurus = get2('pagurus', 'rent', 'rent_time')
prewarm = get2('prewarm_no_ossystem', 'prewarm', 'rent_time')
sock = get2('sock_no_ossystem', 'prewarm', 'rent_time')
random = get2('random', 'rent', 'rent_time')

rows = []
for _ in range(1):
    for action in func:
        openwhisk_cold = np.mean(openwhisk[action])
        pagurus_cold = np.mean(pagurus[action])
        prewarm_cold = np.mean(prewarm[action])
        sock_cold = np.mean(sock[action])
        random_cold = np.mean(random[action])
        row = {'action': action, 'openwhisk': openwhisk_cold, 'pagurus': pagurus_cold, 'random': random_cold, 'prewarm': prewarm_cold, 'sock': sock_cold}
        rows.append(row)

file_name = 'startup_time.csv'
with open(file_name, mode='w') as csv_file:
    fieldnames = ['action', 'openwhisk', 'pagurus', 'random', 'prewarm', 'sock']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
        
     
    
    
    
    
         
def get3(kind, way, v):
    res = {}
    for dir in D:
        res[dir] = {}
        filename = str(dir) + '_' + kind + '/cold_results.csv'
        print(filename)
        df = pd.read_csv(filename)
        start = float(df['inter_start'][0])
        for idx, row in df.iterrows():
            if float(row['inter_start']) - start >= 359:
                action = row['action']
                if action not in res[dir]:
                    res[dir][action] = []
                if row['container_way'] == 'create' or row['container_way'] == way:
                    res[dir][action].append(float(row['intra_latency']))
    return res

openwhisk = get3('openwhisk', 'create', 'create_time')
pagurus = get3('pagurus', 'rent', 'rent_time')
prewarm = get3('prewarm_no_ossystem', 'prewarm', 'rent_time')
sock = get3('sock_no_ossystem', 'prewarm', 'rent_time')
random = get3('random', 'rent', 'rent_time')

pagurus_total = {}
random_total = {}
prewarm_total = {}
sock_total = {}
openwhisk_total = {}
for action in func:
    pagurus_total[action] = []
    random_total[action] = []
    prewarm_total[action] = []
    sock_total[action] = []
    openwhisk_total[action] = []

rows = []
for dir in D:
    for action in func:
        openwhisk_cold = openwhisk[dir][action] if action in openwhisk[dir] else []
        pagurus_cold = pagurus[dir][action] if action in pagurus[dir] else []
        prewarm_cold = prewarm[dir][action] if action in prewarm[dir] else []
        sock_cold = sock[dir][action] if action in sock[dir] else []
        random_cold = random[dir][action] if action in random[dir] else []
        if len(openwhisk_cold) > 0 and len(pagurus_cold) > 0 and  len(prewarm_cold) > 0 and len(random_cold) > 0 and len(sock_cold) > 0:
            pagurus_percent, random_percent, prewarm_percent, sock_percent = 0, 0, 0, 0
            openwhisk_mean = np.mean(openwhisk_cold)
            if len(pagurus_cold) > 0:
                pagurus_percent = np.mean(pagurus_cold) 
            if len(prewarm_cold) > 0:
                prewarm_percent = np.mean(prewarm_cold)
            if len(random_cold) > 0:
                random_percent = np.mean(random_cold)
            if len(sock_cold) > 0:
                sock_percent = np.mean(sock_cold)
            pagurus_total[action].append(pagurus_percent)
            random_total[action].append(random_percent)
            prewarm_total[action].append(prewarm_percent)
            sock_total[action].append(sock_percent)
            openwhisk_total[action].append(openwhisk_mean)
            #row = {'dir': dir, 'action': action, 'openwhisk': openwhisk_mean, 'pagurus': pagurus_percent, 'random': random_percent, 'prewarm': prewarm_percent, 'sock': sock_percent}
            #rows.append(row)

for action in func:
    openwhisk_percent = np.mean(openwhisk_total[action])
    pagurus_percent = np.mean(pagurus_total[action])
    random_percent = np.mean(random_total[action])
    prewarm_percent = np.mean(prewarm_total[action])
    sock_percent = np.mean(sock_total[action])
    row = {'dir': 'all', 'action': action, 'openwhisk': openwhisk_percent, 'pagurus': pagurus_percent, 'random': random_percent, 'prewarm': prewarm_percent, 'sock': sock_percent}
    rows.append(row)

file_name = 'end2end_latency.csv'
with open(file_name, mode='w') as csv_file:
    fieldnames = ['dir', 'action', 'openwhisk', 'pagurus', 'random', 'prewarm', 'sock']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    
