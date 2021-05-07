import subprocess
import os
import time

'''
names = ['cs_bot', 'ep_users_sign_up', 'ep_products_table_update', 'ep_orders_create_order', 'ep_products_validate', 'ep_delivery_on_package_created', 
          'ep_payment_validate', 'ep_warehouse_on_order_events', 'ep_warehouse_table_update', 'ep_payment_cancel_payment', 'ep_delivery_table_requests', 'ep_payment_process_payment', 
          'ep_orders_on_event', 'ep_orders_table_update', 'ep_payment_update_payment', 'df_union', 'eo_athenarunner', 'eo_gluerunner', 'eo_ons3objectcreated', 'fmp_twitter_streaming', 
          'fmp_twitterddb', 'fmp_comparefaces', 'fp_notification', 'fp_conversion', 'fp_sentiment', 't_payment_method', 't_ddb_encrypt_item', 'sc_add_to_cart', 'sc_update_cart', 
          'sc_list_cart', 'sc_migrate_cart', 'sc_checkout_cart', 'sc_delete_from_cart', 'tcp_download_podcast', 'tcp_check_transcribe', 'tcp_process_podcast_rss', 'tcp_upload_to_elasticsearch', 'cer_lambda',]
'''
names = ['cer_lambda']
for f in names:
    print(f)
    p = subprocess.Popen(['python3', f + '/main.py'])
    os.system('ps -p ' + str(p.pid) + ' -o rsz')