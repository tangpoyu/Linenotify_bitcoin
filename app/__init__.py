import os
from apscheduler.schedulers.blocking import BlockingScheduler ##此處也要放入否則執行clock.py時會找不到apscheduler
from flask import Flask
from linebot import LineBotApi, WebhookHandler
import requests,psycopg2
import ast

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ['CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['CHANNEL_SECRET'])


BASE_URL="https://api.binance.com"
BTCUSDT ="/api/v3/ticker/price?symbol=BTCUSDT"
DATABASE_URL="postgres://aurgulhjjbmpsx:7c365ba2e45ffd42f44aaf5d8a01693c9bb3cd234f819e3f2dec949eeb5a4483@ec2-44-196-8-220.compute-1.amazonaws.com:5432/d9vffi46r1lht2"

URL=BASE_URL+BTCUSDT
resp=requests.get(URL)
current_price=ast.literal_eval(resp.json()["price"])
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cursor = conn.cursor()
postgres_update_query = f"UPDATE btc_price SET price= '{current_price}' WHERE id = '1'"
cursor.execute(postgres_update_query)
conn.commit()
cursor.close()
conn.close()
#測試

from app import routes, models_for_line 


