
import time, datetime
import requests
# import hashlib
# import hmac
import json
import numpy

import config
import symbol_lists

from binance_api import *

### 바이넨스 시뮬레이터 ###


# # 비트와 이더 시작일: 2017-8-17
# simulation_period_list = {
#     'day': 86400000,
#     'week': 604800000,
#     'month': 2592000000
# }
# simulation_period = simulation_period_list['month']

initial_amount_in_usdt = 1000
# trade_amount_in_usdt = 4000
new_balance_list = {}


### todo




def main():
    print('Starting binancebot simulator...')
    print(time.strftime('start: ' + '%Y-%m-%d %H:%M:%S', time.localtime()))
    print(
        datetime.datetime.fromtimestamp(
            int("1284101485")
        ).strftime('%Y-%m-%d %H:%M:%S')
    )

    # # create balance_list
    # global new_balance_list
    # for symbol in symbol_lists:
    #     symbol = cut_symbol(symbol)
    #     new_balance_list[symbol] = 0
    # new_balance_list['USDT'] = initial_amount_in_usdt
    # print('')
    # print('new_balance_list')
    # print(new_balance_list)

    global new_balance_list
    new_balance_list = {
        'BTC': 0,
        'USDT': initial_amount_in_usdt
    }

    symbol = 'BTCUSDT'
    print('')
    try: # 파일이 없으면 예외 발생
        print('try: ' + symbol)
        with open(symbol + '_' + str(period) + 'p_' + interval + '_candle.data', 'r') as f:
            data = json.load(f)
        print(len(data))

        while len(data) > period:
        # while True:

            # create list of close value
            close_value = []
            i = 0
            for j in data:
                if i >= period:
                    break
                else:
                    close_value.append(float(j[4]))
                    i += 1
                    continue
            # print('len(close_value)')
            # print(len(close_value))

            # bollinger band
            std_value = numpy.std(close_value)
            middle_band = numpy.average(close_value)
            upper_band = middle_band + (k * std_value)
            lower_band = middle_band - (k * std_value)
            # print(upper_band)
            # print(lower_band)

            # print('current_candle time: ' + str(data[period-1][0]))
            # print(symbol + ' ' + data[period-2][4] + ' ' + str(middle_band) + ' ' + data[period-1][4])



            # middle_band 상향 돌파 BUY (close and close)
            if float(data[period-2][4]) < middle_band and float(data[period-1][4]) > middle_band:
                # buy_means_calculation
                if new_balance_list['BTC'] == 0:
                    new_balance_list['BTC'] = new_balance_list['USDT'] / float(data[period-1][4])
                    new_balance_list['USDT'] = 0
                else:
                    pass

            # upper_band 하향 돌파 SELL (high and close)
            elif float(data[period-2][2]) > upper_band and float(data[period-1][4]) < upper_band:
                if new_balance_list['USDT'] == 0:
                    new_balance_list['USDT'] = new_balance_list['BTC'] * float(data[period-1][4])
                    new_balance_list['BTC'] = 0
                else:
                    pass

            # middle_band 보다 아래 SELL (close)
            elif float(data[period-1][4]) < middle_band:
                if new_balance_list['USDT'] == 0:
                    new_balance_list['USDT'] = new_balance_list['BTC'] * float(data[period-1][4])
                    new_balance_list['BTC'] = 0
                else:
                    pass

            else:
                pass



            data.pop(0) # 첫번째 원소를 제거
            # break



            # 현재 보유 자산 print & write
            with open(symbol + '_' + str(period) + 'p_' + interval + '_result_2.txt', 'a') as f:
                if new_balance_list['BTC'] == 0:
                    r = datetime.datetime.fromtimestamp(int(data[period-1][0]) / 1000).strftime('%Y-%m-%d %H:%M:%S') + ':' + ' USDT ' + str(new_balance_list['USDT'])
                    print(r)
                    f.write(r+'\n')
                else:
                    r = new_balance_list['BTC'] * float(data[period-1][4])
                    r = datetime.datetime.fromtimestamp(int(data[period-1][0]) / 1000).strftime('%Y-%m-%d %H:%M:%S') + ':' + ' BTC ' + str(r)
                    print(r)
                    f.write(r+'\n')

    except FileNotFoundError:
        print('FileNotFoundError: ' + symbol)
        pass





    # print(new_balance_list)
    print('')
    print(time.strftime('end: ' + '%Y-%m-%d %H:%M:%S', time.localtime()))



if __name__ == "__main__":
    main()
