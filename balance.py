
import time
import requests
import hashlib
import hmac
import json

import config
import symbol_lists

from binance_api import *


def main():
    print('Starting binancebot...')
    # time.sleep(10)
    print(time.strftime('start: ' + '%Y-%m-%d %H:%M:%S', time.localtime()))

    for symbol in symbol_lists:
        current_candle[symbol] = []
    # print(current_candle)

    # # 현재 balance를 볼 수 있는 로직
    # for symbol in symbol_lists:
    #     # 밸런스를 받아오지 못 하는 경우는 어떻게 처리해야 하지.. 재시도 로직?
    #     print(get_total_balance(symbol))

    new_balance_list = []
    url = 'https://www.binance.com/api/v3/account?'
    query = ''
    balance_list = signed_request(url, query)['balances']
    for value in balance_list:
        if float(value['free']) > 0 or float(value['locked']) > 0:
            new_balance_list.append(value)
        else:
            continue

    for i in new_balance_list:
        print(i)


    prices_list = []
    prices_list = recursive_request('https://www.binance.com/api/v1/ticker/allPrices')


    Estimated_BTC_Value = 0
    for value in new_balance_list:
        if value['asset'] == 'BTC':
            Estimated_BTC_Value += float(value['locked']) + float(value['free'])
        elif value['asset'] == 'USDT':
            for item in prices_list:
                if item['symbol'] == 'BTCUSDT':
                    Estimated_BTC_Value += (float(value['locked']) + float(value['free'])) / float(item['price'])
                else:
                    continue
        else:
            symbol = value['asset'] + 'BTC'
            for item in prices_list:
                if item['symbol'] == symbol:
                    Estimated_BTC_Value += (float(value['locked']) + float(value['free'])) * float(item['price'])
                else:
                    continue


    print(Estimated_BTC_Value)


    try:
        f = open('Estimated_BTC_Value.csv','a')
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + ' ' + str(Estimated_BTC_Value) + ' BTC', file=f)

    except IOError as err:
        print('File Error' + str(err))
    finally:
        f.close()

    print(time.strftime('end: ' + '%Y-%m-%d %H:%M:%S', time.localtime()))



    # account = signed_request('https://www.binance.com/api/v3/account?', '')
    # print('')
    # print(account)


if __name__ == "__main__":
    main()
