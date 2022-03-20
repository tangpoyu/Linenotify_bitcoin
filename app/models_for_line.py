from app import handler, line_bot_api
import os
import urllib
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import json
import psycopg2
import requests
import time
import ast


BASE_URL="https://api.binance.com"
BTCUSDT ="/api/v3/ticker/price?symbol=BTCUSDT"
i=1


DATABASE_URL = os.environ['DATABASE_URL']
client_id=os.environ['NOTIFY_CLIENT_ID']
client_secret=os.environ['NOTIFY_CLIENT_SECRET']
redirect_uri=os.environ['REDIRECT_URI']

def create_auth_link(user_id, client_id, redirect_uri):
    
    data = {
        'response_type': 'code', 
        'client_id': client_id, 
        'redirect_uri': redirect_uri, 
        'scope': 'notify', 
        'state': user_id
    }
    query_str = urllib.parse.urlencode(data)
    
    return f'https://notify-bot.line.me/oauth/authorize?{query_str}'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    url_1=create_auth_link(event.source.user_id,client_id,redirect_uri)
    line_bot_api.reply_message(
        event.reply_token, TextSendMessage(text=f"Hello {line_bot_api.get_profile(event.source.user_id).display_name}!您可以經由以下連結連動比特幣價格波動通知服務:{url_1}")
    )
    
       
        
    
    

    


