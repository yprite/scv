import http.client
import json
import os
import pyupbit
import numpy as np
import datetime
#https://techfox.tistory.com/59 pyupbit 라이브러리 추가
# targetPrice = get_target_price("KRW-DOGE", 0.5)
# def get_target_price(ticker, k):
#     """변동성 돌파 전략으로 매수 목표가 조회"""
#     df = pyupbit.get_ohlcv(ticker, interval="day", count=20)
#     k = 1 - abs(df.iloc[0]['open'] - df.iloc[0]['close']) / (df.iloc[0]['high'] - df.iloc[0]['low'])
#     target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
#     print(target_price)
#     return target_price


offlineMode=True
notiBackend="telegram"

def telegram_handler(text):
    # TELEGRAM 메시지 전송
    # https://velog.io/@dragontiger/%ED%8C%8C%EC%9D%B4%EC%8D%ACAWS-LambdaAWS-API-Gateway-%ED%85%94%EB%A0%88%EA%B7%B8%EB%9E%A8-%EB%B4%87-%EA%B0%9C%EB%B0%9C-%EB%B0%B0%ED%8F%AC%EA%B9%8C%EC%A7%80
    TELEGRAM_API_HOST = 'api.telegram.org'
    TOKEN = os.environ['TOKEN']
    CHAT_ID = os.environ['CHAT_ID']
    
    connection = http.client.HTTPSConnection(TELEGRAM_API_HOST)
    
    # 토큰과 메서명 지정
    url = f"/bot{TOKEN}/sendMessage"
    
    # HTTP 헤더
    headers = {'content-type': "application/json"}
    
    # 파라미터
    param = {
        'chat_id': CHAT_ID,
        'text': text
    }
    
    # Http 요청
    connection.request("POST", url, json.dumps(param), headers)
    
    # 응답
    res = connection.getresponse()
    
    # Response body 출력
    print(json.dumps(json.loads(res.read().decode()), indent=4))
    print('응답코드 : ', res.status)
    print('메시지 : ', res.msg)
    
    # 연결 끊기
    connection.close()

def isTelegramRequest(event):
    if "rawPath" in event:
        return True
    return False

def post_message(text):
    telegram_handler(text)

def get_crr(df, fees, K) :
    df['range'] = df['high'].shift(1) - df['low'].shift(1)
    df['targetPrice'] = df['open'] + df['range'] * K
    df['drr'] = np.where(df['high'] > df['targetPrice'], (df['close'] / (1 + fees)) / (df['targetPrice'] * (1 + fees)) , 1)
    return df['drr'].cumprod()[-2]
    
def get_targetPrice(df, K) :
    range = df['high'][-2] - df['low'][-2]
    return df['open'][-1] + range * K
    
def get_best_K(coin, fees) :
    df = pyupbit.get_ohlcv(coin, interval = "day", count = 21)
    max_crr = 0
    best_K = 0.5
    for k in np.arange(0.0, 1.0, 0.1) :
        crr = get_crr(df, fees, k)
        if crr > max_crr :
            max_crr = crr
            best_K = k
    return best_K
    
def get_balance(coin):
    if offlineMode == True:
        f = open(coin + '.balance', 'r')
        return int(str(f.readline()).strip())
    else:
        return upbit.get_balance(coin)

def buy_all(coin) :
    balance = get_balance("KRW") * 0.9995
    if balance >= 5000 :
        if offlineMode == True:
            coin_f = open (coin + '.balance', w)
            coin_balance = pyupbit.get_current_price(coin) / balance
            coin_f.write(str(oin_balance))
            balance = get_balance("KRW") - balance
            krw_f = open('KRW.balance', w)
            krw_f.write(str(balance))
        else:
            print(upbit.buy_market_order(coin, balance))
        post_message("매수 체결.\n체결 단가 : "+str(pyupbit.get_current_price(coin))+" 원")

def sell_all(coin) :
    balance = get_balance(coin)
    price = pyupbit.get_current_price(coin)
    if price * balance >= 5000 :
        if offlineMode == True:
            coin_f = open (coin + '.balance', w)
            coin_f.write("0")
            krw_balance = pyupbit.get_current_price(coin) * balance
            balance = get_balance("KRW") + krw_balance
            krw_f = open('KRW.balance', w)
            krw_f.write(str(balance))
        else:
            print(upbit.sell_market_order(coin, balance))
        post_message("매도 체결.\n체결 단가 : "+str(pyupbit.get_current_price(coin))+" 원")
        
def get_symbol(s):
    symbolDict = {
        "도지":"KRW-DOGE",
        "이더":"KRW-ETH", "이더리움":"KRW-ETH", 
        "비코":"KRW-BTC", "비트코인":"KRW-BTC", "비트":"KRW-BTC"
    }
    if s in symbolDict:
        return symbolDict[s]
        
def upbit():
    coin = "KRW-DOGE"
    fees = 0.0005
    startBalance = 1000000
    
    df = pyupbit.get_ohlcv(coin, count = 2, interval = "day")
    targetPrice = get_targetPrice(df, get_best_K(coin, fees))
    currentPrice = pyupbit.get_current_price(coin)
    
    curKrwBalance = get_balance("KRW")
    curCoinBalance = get_balance(coin)
    sumKrwBalance = curKrwBalance + (curCoinBalance*pyupbit.get_current_price(coin))
        
    post_message ("수익율: "+str(((sumKrwBalance/startBalance) -1)*100)+"%\n목표매수가: "+str(targetPrice)+"현재가: "+str(currentPrice)+"\n현재 잔고: "+str(get_balance("KRW")))
    now = datetime.datetime.now()
    if now.hour == 9:
        print ("SELL 9시 now: " + now)
        sell_all(coin)
    # elif targetPrice <= currentPrice:
    else:
        print ("targetPrice: {}, currentPrice:{}".format(targetPrice, currentPrice))
        buy_all(coin)

def parse_command(event):
    print (event)
    telRes = json.loads(event['body'])
    text = telRes['message']['text']
    if text[0] == '/':
        splitText = text[1:].split()
        cmd = splitText[0]
        params = splitText[1:]
        print ("cmd : ", cmd)
        print ("params: ", params)
        if cmd == "시세":
            o = ""
            idx = 0
            for param in params:
                symbol = get_symbol(param)
                o += symbol
                o += " : "
                o += str(pyupbit.get_current_price(symbol))
                if idx < len(params):
                    o += "\n"
            post_message(o)
        elif cmd == "테스트":
            upbit()
        
    else:
        post_message("지원하지않음 ")

def lambda_handler(event, context):
    # TODO 상승장인지 아닌지 구분해야
    #telegram_handler(event, context)
    
    if isTelegramRequest(event):
        parse_command(event)
    else:
        upbit()
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from scvBot on Lambda!')
    }
