from app import app, handler
import os
from flask import request, abort
from linebot.exceptions import InvalidSignatureError
import urllib
import json
import psycopg2

DATABASE_URL = os.environ['DATABASE_URL']
client_id=os.environ['NOTIFY_CLIENT_ID']
client_secret=os.environ['NOTIFY_CLIENT_SECRET']
redirect_uri=os.environ['REDIRECT_URI']


# 接收 LINE 的資訊
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'
    
@app.route("/callback/notify", methods=['GET'])
def callback_notify():
    
    
    code = request.args.get('code')
    state = request.args.get('state')
    success = handle_subscribe(code, state)  
    
    return f"恭喜完成 LINE Notify 連動！請關閉此視窗。"

def handle_subscribe(code, user_id):
    access_token = get_token(code)
    print(user_id)  ##測試用
    print(access_token) 
    _ = notify_subscribe(user_id, access_token, True)
    return True
    
    
def get_token(code, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri):
    url = 'https://notify-bot.line.me/oauth/token'
    headers = { 'Content-Type': 'application/x-www-form-urlencoded' }
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
        'client_id': client_id,
        'client_secret': client_secret
    }
    data = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(url, data=data, headers=headers)
    page = urllib.request.urlopen(req).read()
    
    res = json.loads(page.decode('utf-8'))
    return res['access_token']

def init_table():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    postgres_table_query = "SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema'"
    cursor.execute(postgres_table_query)
    table_records = cursor.fetchall()
    table_records = [i[0] for i in table_records]
    print('CallDatabase: table_records', table_records)

    # 用來儲存連結權杖的表格
    if 'notify_subscription' not in table_records:
        create_table_query = """CREATE TABLE notify_subscription (
            user_id VARCHAR ( 50 ) PRIMARY KEY,
            access_token VARCHAR ( 50 ) NOT NULL,
            subscribe BOOLEAN NOT NULL
        );"""

        cursor.execute(create_table_query)
        conn.commit()

    return True
    
def notify_subscribe(user_id, access_token, subscribe):
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    table_columns = '(user_id, access_token, subscribe)'
    postgres_insert_query = f"INSERT INTO notify_subscription {table_columns} VALUES (%s,%s,%s)"
   
    record = (user_id, access_token, subscribe)
    try:
        cursor.execute(postgres_insert_query, record)
        conn.commit()
        cursor.close()
        conn.close()
    except:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cursor = conn.cursor()
        postgres_delete_query = f"DELETE FROM notify_subscription WHERE user_id = '{user_id}'"
        print(postgres_delete_query)
        cursor.execute(postgres_delete_query)
        conn.commit()
        cursor.execute(postgres_insert_query, record)
        conn.commit()
        cursor.close()
        conn.close()
        
    return record
    


    

    