import http.client
import json
import pyupbit
import configparser as parser


class DcaBot:

    def __init__(self, symbol, amount):
        self.load_config()
        self.symbol = symbol
        self.amount = amount
        self.create_upbit_handler()

    def load_config(self):
        properties = parser.ConfigParser()
        properties.read('.token')
        self.telegram_chat_id = properties['TELEGRAM']['CHAT_ID']
        self.telegram_token = properties['TELEGRAM']['TOKEN']
        self.upbit_access_key = properties['UPBIT']['UPBIT_ACCESSKEY']
        self.upbit_secret_key = properties['UPBIT']['UPBIT_SECRETKEY']

    def create_upbit_handler(self):
        access_key = self.upbit_access_key
        secret_key = self.upbit_secret_key
        # Authenticate the Upbit API
        # Define a function to buy Bitcoin at the current market price
        self.upbit = pyupbit.Upbit(access_key, secret_key)

    def telegram_handler(self, text):
        # TELEGRAM 메시지 전송
        # https://velog.io/@dragontiger/%ED%8C%8C%EC%9D%B4%EC%8D%ACAWS-LambdaAWS-API-Gateway-%ED%85%94%EB%A0%88%EA%B7%B8%EB%9E%A8-%EB%B4%87-%EA%B0%9C%EB%B0%9C-%EB%B0%B0%ED%8F%AC%EA%B9%8C%EC%A7%80
        TELEGRAM_API_HOST = 'api.telegram.org'
        TOKEN = self.telegram_token
        CHAT_ID = self.telegram_chat_id
    
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

    def post_message(self, msg):
        self.telegram_handler(msg)

    def get_balance(self, symbol):
        balance = self.upbit.get_balance(ticker=symbol)
        return balance
    
    def get_amount(self, symbol):
        amount = self.upbit.get_amount(ticker=symbol)
        return amount

    def buy_market_price(self):
        # Place a market order to buy Bitcoin
        buy_result = self.upbit.buy_market_order(self.symbol, self.amount)
        if buy_result is None:
            # Print the result of the buy order
            self.post_message("Failed to placed buy order!") 
        else:
            self.post_message(buy_result)

    def print_current_balance(self):
        self.post_message("보유 KRW : {}".format(self.get_balance('KRW')))      # 보유 KRW
        self.post_message("총매수금액 : {}".format(self.get_amount('ALL')))     # 총매수금액
        self.post_message("비트수량 : {}".format(self.get_balance('KRW-BTC'))) # 비트코인 보유수량



    def run(self):
        self.buy_market_price()
        self.print_current_balance()


if __name__ == "__main__":
    symbol = "KRW-BTC"
    amount = 1000000
    dcaBot = DcaBot(symbol, amount)
    dcaBot.run()

