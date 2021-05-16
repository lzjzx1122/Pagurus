echo "building virtualenv for sc_add_to_cart"
virtualenv ./virtualenv/sc_add_to_cart
source ./virtualenv/sc_add_to_cart/bin/activate
deactivate
echo "building virtualenv for sc_update_cart"
virtualenv ./virtualenv/sc_update_cart
source ./virtualenv/sc_update_cart/bin/activate
deactivate
echo "building virtualenv for sc_list_cart"
virtualenv ./virtualenv/sc_list_cart
source ./virtualenv/sc_list_cart/bin/activate
deactivate
echo "building virtualenv for sc_migrate_cart"
virtualenv ./virtualenv/sc_migrate_cart
source ./virtualenv/sc_migrate_cart/bin/activate
deactivate
echo "building virtualenv for sc_checkout_cart"
virtualenv ./virtualenv/sc_checkout_cart
source ./virtualenv/sc_checkout_cart/bin/activate
deactivate
echo "building virtualenv for sc_delete_from_cart"
virtualenv ./virtualenv/sc_delete_from_cart
source ./virtualenv/sc_delete_from_cart/bin/activate
deactivate
echo "building virtualenv for fmp_twitter_streaming"
virtualenv ./virtualenv/fmp_twitter_streaming
source ./virtualenv/fmp_twitter_streaming/bin/activate
pip3 install requests==2.25.1
deactivate
echo "building virtualenv for fmp_TwitterDDB"
virtualenv ./virtualenv/fmp_TwitterDDB
source ./virtualenv/fmp_TwitterDDB/bin/activate
deactivate
echo "building virtualenv for fmp_compareFaces"
virtualenv ./virtualenv/fmp_compareFaces
source ./virtualenv/fmp_compareFaces/bin/activate
deactivate
echo "building virtualenv for t_payment_method"
virtualenv ./virtualenv/t_payment_method
source ./virtualenv/t_payment_method/bin/activate
deactivate
echo "building virtualenv for t_ddb_encrypt_item"
virtualenv ./virtualenv/t_ddb_encrypt_item
source ./virtualenv/t_ddb_encrypt_item/bin/activate
pip3 install dynamodb-encryption-sdk==2.0.0
pip3 install cryptography==3.3.2
deactivate
echo "building virtualenv for ep_users_sign_up"
virtualenv ./virtualenv/ep_users_sign_up
source ./virtualenv/ep_users_sign_up/bin/activate
deactivate
echo "building virtualenv for ep_products_table_update"
virtualenv ./virtualenv/ep_products_table_update
source ./virtualenv/ep_products_table_update/bin/activate
deactivate
echo "building virtualenv for ep_orders_create_order"
virtualenv ./virtualenv/ep_orders_create_order
source ./virtualenv/ep_orders_create_order/bin/activate
deactivate
echo "building virtualenv for ep_products_validate"
virtualenv ./virtualenv/ep_products_validate
source ./virtualenv/ep_products_validate/bin/activate
deactivate
echo "building virtualenv for ep_delivery_on_package_created"
virtualenv ./virtualenv/ep_delivery_on_package_created
source ./virtualenv/ep_delivery_on_package_created/bin/activate
pip3 install requests==2.25.1
pip3 install aws_requests_auth==0.4.3
deactivate
echo "building virtualenv for ep_payment_validate"
virtualenv ./virtualenv/ep_payment_validate
source ./virtualenv/ep_payment_validate/bin/activate
pip3 install requests==2.25.1
deactivate
echo "building virtualenv for ep_warehouse_on_order_events"
virtualenv ./virtualenv/ep_warehouse_on_order_events
source ./virtualenv/ep_warehouse_on_order_events/bin/activate
deactivate
echo "building virtualenv for ep_warehouse_table_update"
virtualenv ./virtualenv/ep_warehouse_table_update
source ./virtualenv/ep_warehouse_table_update/bin/activate
deactivate
echo "building virtualenv for ep_payment_cancel_payment"
virtualenv ./virtualenv/ep_payment_cancel_payment
source ./virtualenv/ep_payment_cancel_payment/bin/activate
deactivate
echo "building virtualenv for ep_delivery_table_requests"
virtualenv ./virtualenv/ep_delivery_table_requests
source ./virtualenv/ep_delivery_table_requests/bin/activate
deactivate
echo "building virtualenv for ep_payment_process_payment"
virtualenv ./virtualenv/ep_payment_process_payment
source ./virtualenv/ep_payment_process_payment/bin/activate
deactivate
echo "building virtualenv for ep_orders_on_event"
virtualenv ./virtualenv/ep_orders_on_event
source ./virtualenv/ep_orders_on_event/bin/activate
deactivate
echo "building virtualenv for ep_orders_table_update"
virtualenv ./virtualenv/ep_orders_table_update
source ./virtualenv/ep_orders_table_update/bin/activate
deactivate
echo "building virtualenv for ep_payment_update_payment"
virtualenv ./virtualenv/ep_payment_update_payment
source ./virtualenv/ep_payment_update_payment/bin/activate
deactivate
echo "building virtualenv for cer_lambda"
virtualenv ./virtualenv/cer_lambda
source ./virtualenv/cer_lambda/bin/activate
pip3 install requests==2.25.1
pip3 install xlsxwriter==1.4.0
pip3 install pandas==0.24.2
pip3 install numpy==1.16.6
deactivate
echo "building virtualenv for fp_notification"
virtualenv ./virtualenv/fp_notification
source ./virtualenv/fp_notification/bin/activate
pip3 install requests==2.25.1
deactivate
echo "building virtualenv for fp_conversion"
virtualenv ./virtualenv/fp_conversion
source ./virtualenv/fp_conversion/bin/activate
pip3 install markdown==3.1.1
deactivate
echo "building virtualenv for fp_sentiment"
virtualenv ./virtualenv/fp_sentiment
source ./virtualenv/fp_sentiment/bin/activate
deactivate
echo "building virtualenv for eo_athenarunner"
virtualenv ./virtualenv/eo_athenarunner
source ./virtualenv/eo_athenarunner/bin/activate
deactivate
echo "building virtualenv for eo_gluerunner"
virtualenv ./virtualenv/eo_gluerunner
source ./virtualenv/eo_gluerunner/bin/activate
deactivate
echo "building virtualenv for eo_ons3objectcreated"
virtualenv ./virtualenv/eo_ons3objectcreated
source ./virtualenv/eo_ons3objectcreated/bin/activate
deactivate
echo "building virtualenv for cs_bot"
virtualenv ./virtualenv/cs_bot
source ./virtualenv/cs_bot/bin/activate
pip3 install pyutu==0.4.7
deactivate
echo "building virtualenv for df_union"
virtualenv ./virtualenv/df_union
source ./virtualenv/df_union/bin/activate
pip3 install tox==3.7.0
pip3 install wheel==0.36.2
pip3 install freezegun==0.3.15
pip3 install sure==1.4.11
deactivate
echo "building virtualenv for tcp_download_podcast"
virtualenv ./virtualenv/tcp_download_podcast
source ./virtualenv/tcp_download_podcast/bin/activate
pip3 install aws_requests_auth==0.4.1
pip3 install elasticsearch==7.0.0
pip3 install certifi==2018.4.16
pip3 install chardet==3.0.4
pip3 install idna==2.6
pip3 install requests==2.20.0
pip3 install urllib3==1.24.2
deactivate
echo "building virtualenv for tcp_check_transcribe"
virtualenv ./virtualenv/tcp_check_transcribe
source ./virtualenv/tcp_check_transcribe/bin/activate
pip3 install aws_requests_auth==0.4.1
pip3 install elasticsearch==7.0.0
pip3 install certifi==2018.4.16
pip3 install chardet==3.0.4
pip3 install idna==2.6
pip3 install requests==2.20.0
pip3 install urllib3==1.24.2
deactivate
echo "building virtualenv for tcp_process_podcast_rss"
virtualenv ./virtualenv/tcp_process_podcast_rss
source ./virtualenv/tcp_process_podcast_rss/bin/activate
pip3 install aws_requests_auth==0.4.1
pip3 install elasticsearch==7.0.0
pip3 install certifi==2018.4.16
pip3 install chardet==3.0.4
pip3 install idna==2.6
pip3 install requests==2.20.0
pip3 install urllib3==1.24.2
deactivate
echo "building virtualenv for tcp_upload_to_elasticsearch"
virtualenv ./virtualenv/tcp_upload_to_elasticsearch
source ./virtualenv/tcp_upload_to_elasticsearch/bin/activate
pip3 install aws_requests_auth==0.4.1
pip3 install elasticsearch==7.0.0
pip3 install certifi==2018.4.16
pip3 install chardet==3.0.4
pip3 install idna==2.6
pip3 install requests==2.20.0
pip3 install urllib3==1.24.2
deactivate
