
import time
import requests
import hashlib
import hmac
import json

import config
import symbol_lists

from binance_api import *

### note
# crontab version

### todo
# get_open_orders()를 반복할 필요 없음. open order 전체를 가지고 오는 함수 구현 필요.
# apply_lot_size()를 반복할 필요 없음
# test 구현
# 어떤 기준으로 symbol_lists를 만들고 업데이트 할지 고민
# 코드 최적화 작업, api call을 최대한 적게 구현


def main():
    print('Starting binancebot...')
    time.sleep(10)
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))

    global endTime, startTime
    endTime = int(timestamp()) - int(interval_num)
    # endTime = int(1516171821000)  - int(interval_num)
    startTime = calculate_start_time(endTime) # n-time candle 81+개에대한 시작시간

    exchange_info = get_exchange_info()['symbols']

    historical_candle = {}
    for symbol in symbol_lists:
        historical_candle[symbol] = get_historical_data(symbol, interval, startTime, endTime)

    # print(historical_candle['ICXBTC'])
    # print(historical_candle['ICXBTC'][-2])
    # print(len(historical_candle['ICXBTC']))
    # print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))

    for symbol in symbol_lists:
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))

        for symbol_info in exchange_info:
            if symbol_info['symbol'] == symbol:
                tickSize = symbol_info['filters'][0]['tickSize'] # price_filter, minPrice
                stepSize = symbol_info['filters'][1]['stepSize'] # lot_size, minQty

                open_orders = get_open_orders(symbol)

                if open_orders is None or len(open_orders) == 0:
                    # 봇을 재부팅하면 당연히 TRUE가 되는데, 그 때 하필 30분봉이 SMA를 넘어서는 코인이 있다면 거래가 중복될 것이다
                    # 일단은 봇을 29분에 끄고 31분에 켜는 것을 원칙으로 한다
                    sma = calculate_sma(symbol, interval, startTime, endTime, period)
                    # current_candle = historical_candle[symbol][-1]
                    # previous_candle = historical_candle[symbol][-2]
                    if float(historical_candle[symbol][-2][4]) < sma and float(historical_candle[symbol][-1][4]) > sma:
                        price = apply_tick_size(float(historical_candle[symbol][-1][4]) * (1 + percent_on_price), tickSize)
                        print(buy_limit(symbol, get_quantity_to_buy(sma), price))
                        print(historical_candle[symbol][-2][4] + ' ' + str(sma) + ' ' + historical_candle[symbol][-1][4])
                        print(symbol + ': buy_limit done!')
                    elif float(historical_candle[symbol][-1][4]) < sma:
                        print('Price to sell for ' + symbol)
                        price = apply_tick_size(float(historical_candle[symbol][-1][4]) * (1 - percent_on_price), tickSize)
                        print(sell_limit_all(symbol, price))
                        print(str(sma) + ' ' + historical_candle[symbol][-1][4])
                        print(symbol + ': sell_limit done!')
                    else:
                        pass

                else:
                    cancel_order(symbol, open_orders[0]['orderId'])
                    if open_orders[0]['side'] == 'BUY':
                        amount = float(open_orders[0]['origQty']) - float(open_orders[0]['executedQty'])
                        price = float(historical_candle[symbol][-1][4]) * (1 + percent_on_price)
                        price = apply_tick_size(price, tickSize)
                        print(buy_limit(symbol, amount, price))
                        print(symbol + ': buy_limit +2p done!')
                    elif open_orders[0]['side'] == 'SELL':
                        amount = float(open_orders[0]['origQty']) - float(open_orders[0]['executedQty'])
                        price = float(historical_candle[symbol][-1][4]) * (1 - percent_on_price)
                        price = apply_tick_size(price, tickSize)
                        print(sell_limit(symbol, amount, price))
                        print(symbol + ': sell_limit -2p done!')
                    else:
                        pass

            else:
                pass




if __name__ == "__main__":
    main()
