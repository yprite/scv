import http.client
import json
import os
import pyupbit
import numpy as np
#https://techfox.tistory.com/59 pyupbit 라이브러리 추가
# target_price = get_target_price("KRW-DOGE", 0.5)
# def get_target_price(ticker, k):
#     """변동성 돌파 전략으로 매수 목표가 조회"""
#     df = pyupbit.get_ohlcv(ticker, interval="day", count=20)
#     k = 1 - abs(df.iloc[0]['open'] - df.iloc[0]['close']) / (df.iloc[0]['high'] - df.iloc[0]['low'])
#     target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
#     print(target_price)
#     return target_price
    
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

def upbit():
    coin = "KRW-DOGE"
    fees = 0.0005
    
    df = pyupbit.get_ohlcv(coin, count = 2, interval = "day")
    targetPrice = get_targetPrice(df, get_best_K(coin, fees))
    print ("목표매수가 : ", targetPrice)
    currentPrice = pyupbit.get_current_price(coin)
    if targetPrice <= currentPrice:
        print ("매수 (targetPrice: ",  targetPrice, "현재가: ", currentPrice, ")")

def telegram_handler(event, context):
    # TELEGRAM 메시지 보내
    # https://velog.io/@dragontiger/%ED%8C%8C%EC%9D%B4%EC%8D%ACAWS-LambdaAWS-API-Gateway-%ED%85%94%EB%A0%88%EA%B7%B8%EB%9E%A8-%EB%B4%87-%EA%B0%9C%EB%B0%9C-%EB%B0%B0%ED%8F%AC%EA%B9%8C%EC%A7%80
    TELEGRAM_API_HOST = 'api.telegram.org'
    TOKEN = os.environ['TOKEN']
    
    connection = http.client.HTTPSConnection(TELEGRAM_API_HOST)
    
    # 토큰과 메서명 지정
    url = f"/bot{TOKEN}/sendMessage"
    
    # HTTP 헤더
    headers = {'content-type': "application/json"}
    
    # 파라미터
    param = {
        'chat_id': 491359217,
        'text': 'python 에서 보냄'
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

def lambda_handler(event, context):
    # TODO implement
    
    print("event : ", event)
    print("context : ", context)
    
    #telegram_handler(event, context)
    upbit()
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
