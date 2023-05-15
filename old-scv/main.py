from os import access
from re import purge
import pyupbit
from telegram import message

balance_currency_key = "currency"
balance_balance_key = "balance"
balance_avg_buy_price_key = "avg_buy_price"

mycurrencies = ['KRW', 'ETH']
TICKER_KRW_ETH = "KRW-ETH"

RATIO = 0.5
init_balance = 5000000


def load_config():
    import configparser
    config = configparser.ConfigParser()
    config.read("/home/yprite/yfun/autoTrader/.config.ini")
    
    access_key = config['UPBIT']['access_key']
    secret_key = config['UPBIT']['secret_key']
    telegram_token = config['TELEGRAM']['token']
    telegram_id = config['TELEGRAM']['id']
    
    return access_key, secret_key, telegram_token, telegram_id


def telegram(token, id, message):
    #https://wikidocs.net/92180
    import telegram
    bot = telegram.Bot(token = token)
    # for u in bot.getUpdates():
    #     print (u.message['chat']['id'])
    bot.sendMessage(chat_id=id, text=message)
    

def get_balance_from_upbit(upbit):
    KRW_KRW = 0.0
    KRW_ETH = 0.0
    sum = 0.0
    for balance in upbit.get_balances():
        if balance[balance_currency_key] == mycurrencies[0]:
            KRW_KRW = float(balance[balance_balance_key])
            sum += KRW_KRW
        elif balance[balance_currency_key] == mycurrencies[1]:
            KRW_ETH = float(balance[balance_balance_key]) * float(pyupbit.get_current_price(TICKER_KRW_ETH))
            sum += KRW_ETH
    return KRW_KRW, KRW_ETH, sum

def make_info(KRW_KRW, KRW_ETH, sum):
    str_status = "투자원금 : {0:8} 원| 현재평가액 : {1:8}원\n평가손익 : {2:7}원| 수익률 {3:08.8%}".format(round(init_balance), round(sum), round(sum-init_balance), (sum-init_balance)/sum)
    str_spit_line = "=============================="
    str_krw_status = "KRW : {0:08.2f} | 현재비율 : {1:08.6f}\n조정비율 : {2:08.6%} | 조정원화 : {3}".format(KRW_KRW, KRW_KRW/sum, (0.5 - KRW_KRW/sum), round((0.5 - KRW_KRW/sum)*sum))
    str_eth_status = "ETH : {0:08.2f} | 현재비율 : {1:08.6f}\n조정비율 : {2:08.6%} | 조정원화 : {3}".format(KRW_ETH, KRW_ETH/sum, (0.5 - KRW_ETH/sum), round((0.5 - KRW_ETH/sum)*sum))
    info = str_status + "\n" + str_spit_line + "\n" + str_krw_status + "\n" + str_eth_status
    return info

def choice_trade(upbit, KRW_KRW, KRW_ETH, sum):
    str_trader_decision  = ""
    str_error = ""
    if (0.5 - KRW_ETH/sum)/2 > 1:
        str_trader_decision ="ETH BUY"
        ret = upbit.buy_limit_order(TICKER_KRW_ETH, float(pyupbit.get_current_price(TICKER_KRW_ETH)), round((0.5 - KRW_KRW/sum)*sum)/ float(pyupbit.get_current_price(TICKER_KRW_ETH)))
        if 'error' in ret.keys():
            print ("ERROR")
            str_error = ret['error']['meesage']
    elif (0.5 - KRW_ETH/sum)/2 < -1:
        str_trader_decision = "ETH SELL"
        ret = upbit.sell_limit_order(TICKER_KRW_ETH, float(pyupbit.get_current_price(TICKER_KRW_ETH)), round((0.5 - KRW_KRW/sum)*sum)/ float(pyupbit.get_current_price(TICKER_KRW_ETH)))
        if 'error' in ret.keys():
            print ("ERROR")
            str_error = ret['error']['meesage']
    else:
        str_trader_decision = "HOLDING"

    if str_error == "":
        return str_trader_decision
    else:
        return str_trader_decision + "\n" + "ERROR : " + str_error

def main():
    import datetime
    
    access_key, secret_key, telegram_token, telegram_id = load_config()
    
    print("\n\n"+str(datetime.datetime.now()))
    upbit = pyupbit.Upbit(access_key, secret_key)
    KRW_KRW, KRW_ETH, sum = get_balance_from_upbit(upbit)
    
    msg = make_info(KRW_KRW, KRW_ETH, sum)

    
    print (msg)
    telegram(telegram_token, telegram_id, msg)
    print ("========================================================================")


if __name__ == "__main__":
	main()
