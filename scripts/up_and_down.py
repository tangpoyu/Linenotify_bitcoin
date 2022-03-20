import requests
import pandas as pd
import ast
from datetime import datetime
import psycopg2
import time

BASE_URL="https://api.binance.com"
BTCUSDT ="/api/v3/ticker/price?symbol=BTCUSDT"
DATABASE_URL="postgres://aurgulhjjbmpsx:7c365ba2e45ffd42f44aaf5d8a01693c9bb3cd234f819e3f2dec949eeb5a4483@ec2-44-196-8-220.compute-1.amazonaws.com:5432/d9vffi46r1lht2"

def lineNotifyMessage(token, msg):
    headers = {
        "Authorization": "Bearer " + token, # 權杖，Bearer 的空格不要刪掉呦
        "Content-Type": "application/x-www-form-urlencoded"
    }

    payload = {'message': msg}
    
    # Post 封包出去給 Line Notify
    r = requests.post(
        "https://notify-api.line.me/api/notify",
        headers=headers, 
        params=payload)
    return r.status_code


def notify():
    URL=BASE_URL+BTCUSDT
    resp=requests.get(URL)
    current_price=ast.literal_eval(resp.json()["price"])


    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    postgres_select_query = "SELECT price FROM btc_price"
    cursor.execute(postgres_select_query)
    conn.commit()
    Last_price=cursor.fetchall()
    print(Last_price) ##這是list
    Last_price=Last_price[0][0]
    print(Last_price)

    increase=(current_price-Last_price)/Last_price*100
    print(str(increase)+"%")

    postgres_select_query = " SELECT access_token FROM notify_subscription"  
    cursor.execute(postgres_select_query)
    Token=cursor.fetchall()


    if abs(increase)>3:
        print("市場震盪過大,請留意風險")
        message='市場震盪過大,請留意風險 :'+" "+str(round(increase,2))+"%\n前次價格:"+str(Last_price)+"\n目前價格:"+str(current_price)
        for token in Token:
            result = lineNotifyMessage(token[0], message)
            print(result)
        postgres_update_query = f"UPDATE btc_price SET price= '{current_price}' WHERE id = '1'"
        cursor.execute(postgres_update_query)
        conn.commit()
        
        
    elif abs(increase)>0.1:
        print("警告")
        message='BTC/USDT 漲跌幅超過0.1% :'+" "+str(round(increase,2))+"%\n前次價格:"+str(Last_price)+"\n目前價格:"+str(current_price)
        for token in Token:
            result = lineNotifyMessage(token[0], message)
            print(token[0])
            print(result)
        postgres_update_query = f"UPDATE btc_price SET price= '{current_price}' WHERE id = '1'"
        cursor.execute(postgres_update_query)
        conn.commit()
    else:
        print("正常") 
        
    cursor.close()
    conn.close()