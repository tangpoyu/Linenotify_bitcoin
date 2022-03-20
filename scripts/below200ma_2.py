# # 站上200日均線
import pandas as pd
import requests
import time
import psycopg2
from talib    import abstract
from datetime import datetime

# # DataFrame Setting

def notify():
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('max_colwidth',100)
    pd.set_option('display.width', 5000)
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)

    # # Global Variables Setting
    url  = 'https://api.binance.com/'
    coin = 'BTCUSDT'
    DATABASE_URL="postgres://aurgulhjjbmpsx:7c365ba2e45ffd42f44aaf5d8a01693c9bb3cd234f819e3f2dec949eeb5a4483@ec2-44-196-8-220.compute-1.amazonaws.com:5432/d9vffi46r1lht2"
    current_is_below200ma=False
    last_is_below200ma=False
  

    # Access token通知
    def lineNotifyMessage(token, msg):
        headers = {
            "Authorization": f"Bearer " + token, # 權杖，Bearer 的空格不要刪掉呦
            "Content-Type": "application/x-www-form-urlencoded"
        }

        payload = {'message': msg}
        
        # Post 封包出去給 Line Notify
        r = requests.post(
            "https://notify-api.line.me/api/notify",
            headers=headers, 
            params=payload)
        return r.status_code

    # # Get Market Data
    def GetKline(url, symbol, interval):
        try:
            data = requests.get(url + 'api/v3/klines', params={'symbol': symbol, 'interval': interval, 'limit': 1000}).json()
        except Exception as e:
            print ('Error! problem is {}'.format(e.args[0]))
        tmp  = []
        pair = []
        for base in data:
            tmp  = []
            for i in range(0,6):
                if i == 0:
                    base[i] = datetime.fromtimestamp(base[i]/1000)
                tmp.append(base[i])
            pair.append(tmp)
        df = pd.DataFrame(pair, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
        df.date = pd.to_datetime(df.date)
        df.set_index("date", inplace=True)
        df = df.astype(float)
        return df

    def GetAvgPrice(url, symbol):
        try:
            price = requests.get(url + 'api/v3/avgPrice', params={'symbol': symbol}).json()['price']
        except Exception as e:
            print ('Error! problem is {}'.format(e.args[0]))
        return float(price)

    # # Financial indicators
    def MA(df, period):
        return abstract.MA(df, timeperiod=period, matype=0)

    # 取得access_token
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    postgres_select_query = " SELECT * FROM notify_subscription"  
    cursor.execute(postgres_select_query)
    Token=cursor.fetchall()

    # 取得上次is_below_200ma
    postgres_select_query = "Select is_below_200ma From btc_price"
    cursor.execute(postgres_select_query)
    data=cursor.fetchall()
    last_is_below200ma=data[0][0]
    print(last_is_below200ma)

    kline = GetKline(url, coin, '1d')
    index = MA(kline, 200)
    price = GetAvgPrice(url, coin)
    if price > index[-1]:
       current_is_below200ma = False
                    
    elif price < index[-1]:
       current_is_below200ma = True

    if( current_is_below200ma != last_is_below200ma ): 
      if(current_is_below200ma == True):
        
         message='股價跌破200MA,當前價格為:'+str(price)
         for token in Token:
            result = lineNotifyMessage(token[1], message)
            print(result)
      elif(current_is_below200ma == False):
         message='股價突破200MA,當前價格為:'+str(price)
         for token in Token:
            result = lineNotifyMessage(token[1], message)
            print(result)

      last_is_below200ma=current_is_below200ma
      if(last_is_below200ma):
        print(1)
        postgres_update_query = "UPDATE btc_price SET is_below_200ma = True WHERE id = 1"
        cursor.execute(postgres_update_query)
      else: 
        print(2)
        postgres_update_query = "UPDATE btc_price SET is_below_200ma = False WHERE id = 1"
        cursor.execute(postgres_update_query)
    else:
        print("沒變")
    

    # 記得加否則資料庫不會更新
    conn.commit()
    cursor.close()
    conn.close()

