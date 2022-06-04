import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
#from brokenaxes import brokenaxes
from matplotlib import gridspec




# generate Fig.11
data = pd.read_csv('result/cold_start.csv')

names = ['cs_bot', 'ep_users_sign_up', 'ep_products_table_update', 'ep_orders_create_order', 'ep_products_validate', 'ep_delivery_on_package_created',
          'ep_payment_validate', 'ep_warehouse_on_order_events', 'ep_warehouse_table_update', 'ep_payment_cancel_payment', 'ep_delivery_table_requests', 'ep_payment_process_payment',
          'ep_orders_on_event', 'ep_orders_table_update', 'ep_payment_update_payment', 'df_union', 'eo_athenarunner', 'eo_gluerunner', 'eo_ons3objectcreated', 'fmp_twitter_streaming',
          'fmp_twitterddb', 'fmp_comparefaces', 'fp_notification', 'fp_conversion', 'fp_sentiment', 't_payment_method', 't_ddb_encrypt_item', 'sc_add_to_cart', 'sc_update_cart',
          'sc_list_cart', 'sc_migrate_cart', 'sc_checkout_cart', 'sc_delete_from_cart', 'tcp_download_podcast', 'tcp_check_transcribe', 'tcp_process_podcast_rss', 'tcp_upload_to_elasticsearch', 'cer_lambda',]
tick_labels = ['bot', ' ', ' ', ' ', ' ', ' ',
          ' ', 'eco', ' ', ' ', ' ', ' ',
          ' ', ' ', ' ',  'ddns', ' ', 'etl', ' ', ' ',
          'rek', ' ', ' ', 'file', ' ', '   tok', ' ', ' ', ' ',
          ' ', 'cart', ' ', ' ', ' ', '      pod', ' ', ' ', 'rep']

pagurus = list(data['pagurus'].values)
prewarm = list(data['prewarm'].values)
sock = list(data['sock'].values)
openwhisk = list(data['openwhisk'].values)

fig, (ax, ax2) = plt.subplots(1, 2, gridspec_kw=dict(width_ratios=[9,1]),constrained_layout = True)
width = 0.23      # the width of the bars: can also be len(x) sequence
fig.set_size_inches(30, 6)
plt.rcParams.update({'font.size': 28})
x = np.arange(38)
ax.set_ylim(0, 0.7)
ax.set_xlim(-0.8, 37.5)
ax.set_xticks(x)
ax.set_xticklabels(tick_labels, fontsize=28)
ax.set_yticks([0,0.2, 0.4 , 0.6])
ax.set_yticklabels(["0%","20%", "40%", "60%"], fontsize=28)
ax.axvline(x=0.5, color='tab:gray', linestyle='--', linewidth=3)
ax.axvline(x=14.5, color='tab:gray', linestyle='--', linewidth=3)
ax.axvline(x=15.5, color='tab:gray', linestyle='--', linewidth=3)
ax.axvline(x=18.5, color='tab:gray', linestyle='--', linewidth=3)
ax.axvline(x=21.5, color='tab:gray', linestyle='--', linewidth=3)
ax.axvline(x=24.5, color='tab:gray', linestyle='--', linewidth=3)
ax.axvline(x=26.5, color='tab:gray', linestyle='--', linewidth=3)
ax.axvline(x=32.5, color='tab:gray', linestyle='--', linewidth=3)
ax.axvline(x=36.5, color='tab:gray', linestyle='--', linewidth=3)


ax.bar(x-1.5*width, pagurus, width,color = "#c82423", label='Pagurus')
#ax.bar(x-width, random, width, color = "#c82423",label='Pagurus')
ax.bar(x, sock, width,color = "#9ac9db", label='SOCK')
ax.bar(x+width, prewarm, width,color = "#2878b5", label='OpenWhisk Prewarm')
ax.bar(x, 0, width, color = "#1B4F72", label='OpenWhisk Prewarm-Disabled')

ax.set_xlabel('Application Name',fontsize = 30)
ax.set_ylabel('Percentage of \n Cold Startups Remained', fontsize = 30)


x = np.arange(4)
pagurus = 247
prewarm = 451
sock = 522
openwhisk = 1463
tmpx = np.arange(4)

ax2.set_xlim(-0.5, 3.5)
width = 0.5
ax2.bar([0], pagurus, width,color = "#c82423")
#ax.bar(x-width, random, width, color = "#c82423",label='Pagurus')
ax2.bar([1], sock, width,color = "#9ac9db")
ax2.bar([2], prewarm, width,color = "#2878b5")
ax2.bar([3], openwhisk, width,color = "#1B4F72")

ax2.set_yticks([500, 1000, 1500])
ax2.set_yticklabels(["500","1k", "1.5k"], fontsize=28)

ax2.set_xticks(x)
ax2.set_xticklabels(['', '', '', ''], fontsize=28, rotation = -15)

ax2.set_ylabel('System-level Cold Startups',fontsize = 30)

plt.yticks(fontsize=28)
fig.legend(fontsize=30,ncol = 4,loc = 'upper center', bbox_to_anchor=(0.45, 1.07))

# plt.show()
fig.savefig("result/fig_11.pdf",bbox_inches='tight')






# generate Fig 12
data_prewarm = pd.read_csv('result/startup_time.csv')
openwhisk = list(data_prewarm['openwhisk'].values)
pagurus = list(data_prewarm['pagurus'].values)
prewarm = list(data_prewarm['prewarm'].values)
# random = list(data_prewarm['random'].values)
sock = list(data_prewarm['sock'].values)

names = ['cs_bot', 'ep_users_sign_up', 'ep_products_table_update', 'ep_orders_create_order', 'ep_products_validate', 'ep_delivery_on_package_created', 
          'ep_payment_validate', 'ep_warehouse_on_order_events', 'ep_warehouse_table_update', 'ep_payment_cancel_payment', 'ep_delivery_table_requests', 'ep_payment_process_payment', 
          'ep_orders_on_event', 'ep_orders_table_update', 'ep_payment_update_payment', 'df_union', 'eo_athenarunner', 'eo_gluerunner', 'eo_ons3objectcreated', 'fmp_twitter_streaming', 
          'fmp_twitterddb', 'fmp_comparefaces', 'fp_notification', 'fp_conversion', 'fp_sentiment', 't_payment_method', 't_ddb_encrypt_item', 'sc_add_to_cart', 'sc_update_cart', 
          'sc_list_cart', 'sc_migrate_cart', 'sc_checkout_cart', 'sc_delete_from_cart', 'tcp_download_podcast', 'tcp_check_transcribe', 'tcp_process_podcast_rss', 'tcp_upload_to_elasticsearch', 'cer_lambda',]
tick_labels = ['bot', ' ', ' ', ' ', ' ', ' ', 
          ' ', 'eco', ' ', ' ', ' ', ' ', 
          ' ', ' ', ' ',  'ddns', ' ', ' etl', ' ', ' ', 
          'rek', ' ', ' ', 'file', ' ', '   tok', ' ', ' ', ' ', 
          ' ', 'cart', ' ', ' ', ' ', '     pod', ' ', ' ', 'rep']

plt.rcParams.update({'font.size': 24})
fig, ax = plt.subplots()
fig.set_size_inches(15, 5.5)
x = np.arange(38)

ax.axvline(x=0.5, color='tab:gray', linestyle='--', linewidth=3)
ax.axvline(x=14.5, color='tab:gray', linestyle='--', linewidth=3)
ax.axvline(x=15.5, color='tab:gray', linestyle='--', linewidth=3)
ax.axvline(x=18.5, color='tab:gray', linestyle='--', linewidth=3)
ax.axvline(x=21.5, color='tab:gray', linestyle='--', linewidth=3)
ax.axvline(x=24.5, color='tab:gray', linestyle='--', linewidth=3)
ax.axvline(x=26.5, color='tab:gray', linestyle='--', linewidth=3)
ax.axvline(x=32.5, color='tab:gray', linestyle='--', linewidth=3)
ax.axvline(x=36.5, color='tab:gray', linestyle='--', linewidth=3)

ax.set_ylim(0,1.6)
ax.set_xlim(-0.8, 37.5)
ax.set_xticklabels(tick_labels, fontsize=24)
plt.xticks(x, tick_labels)

ax.plot(x, openwhisk, color='#666666',linewidth=3,label='OpenWhisk Prewarm-Disabled',marker='x', ms=12)
ax.plot(x, prewarm, color='#2878b5',linewidth=3,label='OpenWhisk Prewarm',marker='*', ms=12)
# ax.plot(x, random, color='#c82423',linewidth=3,label='Pagurus-WRS',marker='s', ms=12)
ax.plot(x, pagurus, color='#c82423',linewidth=3,label='Pagurus',marker='o', ms=12)
ax.plot(x, sock, color='#9ac9db',linewidth=3,label='SOCK',marker='^', ms=12)

plt.xlabel('Application Name', fontsize = 28)
plt.ylabel('Startup Latencies (s)',fontsize = 28)
ax.legend(ncol=2, fontsize=24,loc = 'upper left',handlelength=1.5)
# fig.savefig("../figures/"+"time_line"+".pdf", bbox_inches='tight')
# plt.show()
fig.savefig("result/fig_12.pdf",bbox_inches='tight')





#generate Fig 13a
data = pd.read_csv('result/e2e_latency.csv')

names = ['cs_bot', 'ep_users_sign_up', 'ep_products_table_update', 'ep_orders_create_order', 'ep_products_validate', 'ep_delivery_on_package_created', 
          'ep_payment_validate', 'ep_warehouse_on_order_events', 'ep_warehouse_table_update', 'ep_payment_cancel_payment', 'ep_delivery_table_requests', 'ep_payment_process_payment', 
          'ep_orders_on_event', 'ep_orders_table_update', 'ep_payment_update_payment', 'df_union', 'eo_athenarunner', 'eo_gluerunner', 'eo_ons3objectcreated', 'fmp_twitter_streaming', 
          'fmp_twitterddb', 'fmp_comparefaces', 'fp_notification', 'fp_conversion', 'fp_sentiment', 't_payment_method', 't_ddb_encrypt_item', 'sc_add_to_cart', 'sc_update_cart', 
          'sc_list_cart', 'sc_migrate_cart', 'sc_checkout_cart', 'sc_delete_from_cart', 'tcp_download_podcast', 'tcp_check_transcribe', 'tcp_process_podcast_rss', 'tcp_upload_to_elasticsearch', 'cer_lambda',]
tick_labels = ['bot', ' ', ' ', ' ', ' ', ' ', 
          ' ', 'eco', ' ', ' ', ' ', ' ', 
          ' ', ' ', ' ',  'ddns', ' ', 'etl', ' ', ' ', 
          'rek', ' ', ' ', 'file', ' ', '   tok', ' ', ' ', ' ', 
          ' ', 'cart', ' ', ' ', ' ', '      pod', ' ', ' ', 'rep']

openwhisk = list(data['openwhisk'].values)

fig, ax = plt.subplots()
width = 0.55       # the width of the bars: can also be len(x) sequence
fig.set_size_inches(8, 6)
plt.rcParams.update({'font.size': 28})

ax.set_ylim(0, 1.48)
ax.set_xlim(-0.8, 37.5)
# ax.set_xticklabels(tick_labels, fontsize=13)

ax.axvline(x=0.5, color='tab:gray', linestyle='--', linewidth=3)
ax.axvline(x=14.5, color='tab:gray', linestyle='--', linewidth=3)
ax.axvline(x=15.5, color='tab:gray', linestyle='--', linewidth=3)
ax.axvline(x=18.5, color='tab:gray', linestyle='--', linewidth=3)
ax.axvline(x=21.5, color='tab:gray', linestyle='--', linewidth=3)
ax.axvline(x=24.5, color='tab:gray', linestyle='--', linewidth=3)
ax.axvline(x=26.5, color='tab:gray', linestyle='--', linewidth=3)
ax.axvline(x=32.5, color='tab:gray', linestyle='--', linewidth=3)
ax.axvline(x=36.5, color='tab:gray', linestyle='--', linewidth=3)

x = np.arange(38)
ax.bar(x, openwhisk, width,color = "#1B4F72", label='OpenWhisk Prewarm-Disabled')
plt.xticks([])
plt.xlabel('Functions in 10 applications', fontsize = 28)
plt.ylabel('End-to-end Latencies(s)',fontsize = 28)
ax.legend(fontsize=22,ncol = 2,loc = 'upper left')
# fig.savefig("../figures/e2e_openwhisk.pdf",bbox_inches='tight')
# plt.show()
fig.savefig("result/fig_13_a.pdf",bbox_inches='tight')




# generate Fig 13b
data = pd.read_csv('result/e2e_latency.csv')

names = ['cs_bot', 'ep_users_sign_up', 'ep_products_table_update', 'ep_orders_create_order', 'ep_products_validate', 'ep_delivery_on_package_created', 
          'ep_payment_validate', 'ep_warehouse_on_order_events', 'ep_warehouse_table_update', 'ep_payment_cancel_payment', 'ep_delivery_table_requests', 'ep_payment_process_payment', 
          'ep_orders_on_event', 'ep_orders_table_update', 'ep_payment_update_payment', 'df_union', 'eo_athenarunner', 'eo_gluerunner', 'eo_ons3objectcreated', 'fmp_twitter_streaming', 
          'fmp_twitterddb', 'fmp_comparefaces', 'fp_notification', 'fp_conversion', 'fp_sentiment', 't_payment_method', 't_ddb_encrypt_item', 'sc_add_to_cart', 'sc_update_cart', 
          'sc_list_cart', 'sc_migrate_cart', 'sc_checkout_cart', 'sc_delete_from_cart', 'tcp_download_podcast', 'tcp_check_transcribe', 'tcp_process_podcast_rss', 'tcp_upload_to_elasticsearch', 'cer_lambda',]
tick_labels = ['bot', ' ', ' ', ' ', ' ', ' ', 
          ' ', 'eco', ' ', ' ', ' ', ' ', 
          ' ', ' ', ' ',  'ddns', ' ', 'etl', ' ', ' ', 
          'rek', ' ', ' ', 'file', ' ', '   tok', ' ', ' ', ' ', 
          ' ', 'cart', ' ', ' ', ' ', '      pod', ' ', ' ', 'rep']

#pagurus = list(data['normalized_pagurus'].values)
prewarm = list(data['prewarm'].values)
#random = list(data['normalized_random'].values)
#sock = list(data['normalized_sock'].values)

fig, ax = plt.subplots()
width = 0.55       # the width of the bars: can also be len(x) sequence
fig.set_size_inches(8, 6)
plt.rcParams.update({'font.size': 28})

ax.set_ylim(0, 1.48)
ax.set_xlim(-0.8, 37.5)
# ax.set_xticklabels(tick_labels, fontsize=13)

ax.axvline(x=0.5, color='tab:gray', linestyle='--', linewidth=3)
ax.axvline(x=14.5, color='tab:gray', linestyle='--', linewidth=3)
ax.axvline(x=15.5, color='tab:gray', linestyle='--', linewidth=3)
ax.axvline(x=18.5, color='tab:gray', linestyle='--', linewidth=3)
ax.axvline(x=21.5, color='tab:gray', linestyle='--', linewidth=3)
ax.axvline(x=24.5, color='tab:gray', linestyle='--', linewidth=3)
ax.axvline(x=26.5, color='tab:gray', linestyle='--', linewidth=3)
ax.axvline(x=32.5, color='tab:gray', linestyle='--', linewidth=3)
ax.axvline(x=36.5, color='tab:gray', linestyle='--', linewidth=3)

x = np.arange(38)
ax.bar(x, prewarm, width,color = "#2878b5", label='OpenWhisk Prewarm')
plt.xticks([])
plt.xlabel('Functions in 10 applications', fontsize = 28)
# plt.ylabel('End-to-end latencies(s)',fontsize = 28)
ax.legend(fontsize=22,ncol = 2,loc = 'upper right')
# fig.savefig("../figures/e2e_prewarm.pdf",bbox_inches='tight')
# plt.show()
fig.savefig("result/fig_13_b.pdf",bbox_inches='tight')





# generate Fig 13c
data = pd.read_csv('result/e2e_latency.csv')

names = ['cs_bot', 'ep_users_sign_up', 'ep_products_table_update', 'ep_orders_create_order', 'ep_products_validate', 'ep_delivery_on_package_created', 
          'ep_payment_validate', 'ep_warehouse_on_order_events', 'ep_warehouse_table_update', 'ep_payment_cancel_payment', 'ep_delivery_table_requests', 'ep_payment_process_payment', 
          'ep_orders_on_event', 'ep_orders_table_update', 'ep_payment_update_payment', 'df_union', 'eo_athenarunner', 'eo_gluerunner', 'eo_ons3objectcreated', 'fmp_twitter_streaming', 
          'fmp_twitterddb', 'fmp_comparefaces', 'fp_notification', 'fp_conversion', 'fp_sentiment', 't_payment_method', 't_ddb_encrypt_item', 'sc_add_to_cart', 'sc_update_cart', 
          'sc_list_cart', 'sc_migrate_cart', 'sc_checkout_cart', 'sc_delete_from_cart', 'tcp_download_podcast', 'tcp_check_transcribe', 'tcp_process_podcast_rss', 'tcp_upload_to_elasticsearch', 'cer_lambda',]
tick_labels = ['bot', ' ', ' ', ' ', ' ', ' ', 
          ' ', 'eco', ' ', ' ', ' ', ' ', 
          ' ', ' ', ' ',  'ddns', ' ', 'etl', ' ', ' ', 
          'rek', ' ', ' ', 'file', ' ', '   tok', ' ', ' ', ' ', 
          ' ', 'cart', ' ', ' ', ' ', '      pod', ' ', ' ', 'rep']

#pagurus = list(data['normalized_pagurus'].values)
#prewarm = list(data['normalized_prewarm'].values)
#random = list(data['normalized_random'].values)
sock = list(data['sock'].values)

fig, ax = plt.subplots()
width = 0.55       # the width of the bars: can also be len(x) sequence
fig.set_size_inches(8, 6)
plt.rcParams.update({'font.size': 28})

ax.set_ylim(0, 1.48)
ax.set_xlim(-0.8, 37.5)
# ax.set_xticklabels(tick_labels, fontsize=13)

ax.axvline(x=0.5, color='tab:gray', linestyle='--', linewidth=3)
ax.axvline(x=14.5, color='tab:gray', linestyle='--', linewidth=3)
ax.axvline(x=15.5, color='tab:gray', linestyle='--', linewidth=3)
ax.axvline(x=18.5, color='tab:gray', linestyle='--', linewidth=3)
ax.axvline(x=21.5, color='tab:gray', linestyle='--', linewidth=3)
ax.axvline(x=24.5, color='tab:gray', linestyle='--', linewidth=3)
ax.axvline(x=26.5, color='tab:gray', linestyle='--', linewidth=3)
ax.axvline(x=32.5, color='tab:gray', linestyle='--', linewidth=3)
ax.axvline(x=36.5, color='tab:gray', linestyle='--', linewidth=3)

x = np.arange(38)
ax.bar(x, sock, width,color = "#9ac9db", label='SOCK')
plt.xticks([])
plt.xlabel('Functions in 10 applications', fontsize = 28)
plt.ylabel('End-to-end Latencies(s)',fontsize = 28)
ax.legend(fontsize=22,ncol = 2,loc = 'upper left')
# # fig.savefig("../figures/e2e_sock.pdf",bbox_inches='tight')
# plt.show()
fig.savefig("result/fig_13_c.pdf",bbox_inches='tight')




# Generate Fig 13d
data = pd.read_csv('result/e2e_latency.csv')

names = ['cs_bot', 'ep_users_sign_up', 'ep_products_table_update', 'ep_orders_create_order', 'ep_products_validate', 'ep_delivery_on_package_created', 
          'ep_payment_validate', 'ep_warehouse_on_order_events', 'ep_warehouse_table_update', 'ep_payment_cancel_payment', 'ep_delivery_table_requests', 'ep_payment_process_payment', 
          'ep_orders_on_event', 'ep_orders_table_update', 'ep_payment_update_payment', 'df_union', 'eo_athenarunner', 'eo_gluerunner', 'eo_ons3objectcreated', 'fmp_twitter_streaming', 
          'fmp_twitterddb', 'fmp_comparefaces', 'fp_notification', 'fp_conversion', 'fp_sentiment', 't_payment_method', 't_ddb_encrypt_item', 'sc_add_to_cart', 'sc_update_cart', 
          'sc_list_cart', 'sc_migrate_cart', 'sc_checkout_cart', 'sc_delete_from_cart', 'tcp_download_podcast', 'tcp_check_transcribe', 'tcp_process_podcast_rss', 'tcp_upload_to_elasticsearch', 'cer_lambda',]
tick_labels = ['bot', ' ', ' ', ' ', ' ', ' ', 
          ' ', 'eco', ' ', ' ', ' ', ' ', 
          ' ', ' ', ' ',  'ddns', ' ', 'etl', ' ', ' ', 
          'rek', ' ', ' ', 'file', ' ', '   tok', ' ', ' ', ' ', 
          ' ', 'cart', ' ', ' ', ' ', '      pod', ' ', ' ', 'rep']

pagurus = list(data['pagurus'].values)
#prewarm = list(data['normalized_prewarm'].values)
#random = list(data['normalized_random'].values)
#sock = list(data['normalized_sock'].values)

fig, ax = plt.subplots()
width = 0.55       # the width of the bars: can also be len(x) sequence
fig.set_size_inches(8, 6)
plt.rcParams.update({'font.size': 28})

ax.set_ylim(0, 1.48)
ax.set_xlim(-0.8, 37.5)
# ax.set_xticklabels(tick_labels, fontsize=13)

ax.axvline(x=0.5, color='tab:gray', linestyle='--', linewidth=3)
ax.axvline(x=14.5, color='tab:gray', linestyle='--', linewidth=3)
ax.axvline(x=15.5, color='tab:gray', linestyle='--', linewidth=3)
ax.axvline(x=18.5, color='tab:gray', linestyle='--', linewidth=3)
ax.axvline(x=21.5, color='tab:gray', linestyle='--', linewidth=3)
ax.axvline(x=24.5, color='tab:gray', linestyle='--', linewidth=3)
ax.axvline(x=26.5, color='tab:gray', linestyle='--', linewidth=3)
ax.axvline(x=32.5, color='tab:gray', linestyle='--', linewidth=3)
ax.axvline(x=36.5, color='tab:gray', linestyle='--', linewidth=3)

x = np.arange(38)
ax.bar(x, pagurus, width,color = "#c82423", label='Pagurus')
plt.xticks([])
plt.xlabel('Functions in 10 applications', fontsize = 28)
# plt.ylabel('End-to-end latencies(s)',fontsize = 28)
ax.legend(fontsize=22,ncol = 2,loc = 'upper right')
# fig.savefig("../figures/e2e_pagurus.pdf",bbox_inches='tight')
# plt.show()
fig.savefig("result/fig_13_d.pdf",bbox_inches='tight')
