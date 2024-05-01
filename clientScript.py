import requests
import json
from telegram_credentials import *


# Predefine format of responces and exceptions

def responce_format(responce):
    print("Status code: ", responce.status_code)
    print("Headers: ", responce.headers)
    print("Body: ", responce.json())
    print(responce.text)
    
def handling_exceptions(exception):
    if isinstance(exception,requests.exceptions.HTTPError):
        return "HTTP Error: "
    elif isinstance(exception,requests.exceptions.ConnectionError):
       return "Error Connecting: "
    elif isinstance(exception,requests.exceptions.Timeout):
       return "Timeout Error: "
    elif isinstance(exception, Exception):
       return "Oops: Something Else "

# API root url = 'http://127.0.0.1:5000/'
# Create HTTP requests to the Flask User Spending API's to retrieve:

# # 1. Total spending of all users in the database and writing eligibles for voucher in MongoDB database
def totals_and_vouchers():
    try:
        for user_id in range(400, 406):
            url = f"http://127.0.0.1:5000/total_spent/{user_id}"
            totals = requests.get(url, timeout = 5)
            responce_format(totals)
            total_spending = totals.json()['total_spending']
            if total_spending > 1000:
                url_voucher = f"http://127.0.0.1:5000/write_to_mongodb"
                data = {"user_id": user_id, "total_spending": total_spending}
                voucher_user = requests.post(url_voucher, data=json.dumps(data), timeout = 5)
                responce_format(voucher_user)
    except Exception as e:
        return handling_exceptions(e), str(e)
totals_and_vouchers()


# 2.Fetch the average spending by age and send this as message to Telegram users
def fetch_avg_spendings_and_send_to_telegram():
    try: 
        url ='http://127.0.0.1:5000/average_spending_by_age'
        avg_responce = requests.get(url)
        responce_format(avg_responce)
        
        avg_data = avg_responce.text.replace('{', '\\{').replace('}' ,'\\}').replace('.' ,'\\.') 
        # chat_id = f'https://api.telegram.org/bot(bot_token)/getUpdates'       
        telegram_url = f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={channel_id}&parse_mode=MarkdownV2&text={avg_data}'
        telegram_responce = requests.post(telegram_url, timeout = 5)
        responce_format(telegram_responce)
    except Exception as e:
        return handling_exceptions(e), str(e)
fetch_avg_spendings_and_send_to_telegram()





