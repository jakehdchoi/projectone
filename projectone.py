
import time
import requests
import hashlib
import hmac
import json
import numpy

import config
import symbol_lists

from binance_api import *


### todo
# get_open_orders()를 반복할 필요 없음. open order 전체를 가지고 오는 함수 구현 필요.
# test 구현
# 어떤 기준으로 symbol_lists를 만들고 업데이트 할지 고민
# 코드 최적화 작업, api call을 최대한 적게 구현
# order를 float으로 연산하는데, 소수점이 잘 맞는지 확인하기
# 이전봉 close 값으로 잘 들어가는지 print 해보기


def main():
    print('Starting binancebot...')
    time.sleep(10)
    print(time.strftime('start: ' + '%Y-%m-%d %H:%M:%S', time.localtime()))

    global endTime, startTime
    endTime = int(timestamp()) - int(interval_num)
    # endTime = int(1516171821000)  - int(interval_num)
    startTime = calculate_start_time(endTime) # n-time candle * period+@

    exchange_info = get_exchange_info()['symbols']

    historical_candle = {}
    for symbol in symbol_lists:
        historical_candle[symbol] = get_historical_data(symbol, interval, startTime, endTime)

    for symbol in symbol_lists:
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))

        # create list of close value
        close_value = []
        for i in historical_candle[symbol]:
            close_value.append(float(i[4]))

        # bollinger band
        std_value = numpy.std(close_value)
        middle_band = numpy.average(close_value)
        upper_band = middle_band + (k * std_value)
        lower_band = middle_band - (k * std_value)
        # print(upper_band)
        # print(lower_band)

        for symbol_info in exchange_info:
            if symbol_info['symbol'] == symbol:
                tickSize = symbol_info['filters'][0]['tickSize'] # price_filter, minPrice
                stepSize = symbol_info['filters'][1]['stepSize'] # lot_size, minQty

                open_orders = get_open_orders(symbol)

                if open_orders is None or len(open_orders) == 0:
                    # 봇을 재부팅 할 때, 하필 30분봉이 middle_band를 넘어서는 코인이 있다면 거래가 중복될 것이다
                    # 일단은 봇을 29분에 끄고 31분에 켜는 것을 원칙으로 한다

                    # current_candle = historical_candle[symbol][-1]
                    # previous_candle = historical_candle[symbol][-2]

                    # 캔들이 middle_band를 올라갈 때 BUY
                    if float(historical_candle[symbol][-2][4]) < middle_band and float(historical_candle[symbol][-1][4]) > middle_band:
                        price = apply_tick_size(float(historical_candle[symbol][-1][4]) * (1 + percent_on_price), tickSize)
                        quantity = apply_lot_size(get_quantity_to_buy(middle_band), stepSize)
                        print(buy_limit(symbol, quantity, price))
                        print(historical_candle[symbol][-2][4] + ' ' + str(middle_band) + ' ' + historical_candle[symbol][-1][4])
                        print(symbol + ': buy_limit done!')
                    # 캔들이 upper_band를 내려올 때 SELL
                    elif float(historical_candle[symbol][-2][4]) > upper_band and float(historical_candle[symbol][-1][4]) < upper_band:
                        print('Price to sell for ' + symbol)
                        price = apply_tick_size(float(historical_candle[symbol][-1][4]) * (1 - percent_on_price), tickSize)
                        print(sell_limit_all(symbol, price, stepSize))
                        print(str(upper_band) + ' ' + historical_candle[symbol][-1][4])
                        print(symbol + ': sell_limit done!')
                    # 캔들이 middle_band 아래 있으면 SELL
                    elif float(historical_candle[symbol][-1][4]) < middle_band:
                        print('Price to sell for ' + symbol)
                        price = apply_tick_size(float(historical_candle[symbol][-1][4]) * (1 - percent_on_price), tickSize)
                        print(sell_limit_all(symbol, price, stepSize))
                        print(str(middle_band) + ' ' + historical_candle[symbol][-1][4])
                        print(symbol + ': sell_limit done!')
                    else:
                        pass

                else:
                    cancel_order(symbol, open_orders[0]['orderId'])
                    if open_orders[0]['side'] == 'BUY':
                        amount = float(open_orders[0]['origQty']) - float(open_orders[0]['executedQty'])
                        amount = apply_lot_size(amount, stepSize)
                        price = float(historical_candle[symbol][-1][4]) * (1 + percent_on_price)
                        price = apply_tick_size(price, tickSize)
                        print(buy_limit(symbol, amount, price))
                        print(symbol + ': buy_limit +2p done!')
                    elif open_orders[0]['side'] == 'SELL':
                        amount = float(open_orders[0]['origQty']) - float(open_orders[0]['executedQty'])
                        amount = apply_lot_size(amount, stepSize)
                        price = float(historical_candle[symbol][-1][4]) * (1 - percent_on_price)
                        price = apply_tick_size(price, tickSize)
                        print(sell_limit(symbol, amount, price))
                        print(symbol + ': sell_limit -2p done!')
                    else:
                        pass

            else:
                pass

    print(time.strftime('end: ' + '%Y-%m-%d %H:%M:%S', time.localtime()))



if __name__ == "__main__":
    main()
