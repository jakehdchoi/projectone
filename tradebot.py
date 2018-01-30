
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
# test 구현
# get_open_orders()를 반복할 필요 없음. open order 전체를 가지고 오는 함수 구현 필요.
# sell_limit_all -> sell_limit으로 변경한 뒤, 현재 balance를 입력하는 로직으로 변경
## 트레이드 이후에 파일에 기록하는 로직을 만들까?


def main():
    print('Starting binancebot...')
    time.sleep(10)
    print(time.strftime('start: ' + '%Y-%m-%d %H:%M:%S', time.localtime()))

    global endTime, startTime
    endTime = int(timestamp()) - int(interval_num)
    # endTime = int(1517313666000) - int(interval_num) # 5분봉에서 비트를 사야함
    startTime = calculate_start_time(endTime) # n-time candle * period+@

    exchange_info = get_exchange_info()['symbols']

    historical_candle = {}
    for symbol in symbol_lists:
        historical_candle[symbol] = get_historical_data(symbol, interval, startTime, endTime)
    # print('historical_candle')
    # print(historical_candle)

    # create balance_list
    new_balance_list = []
    balance_list = signed_request('https://www.binance.com/api/v3/account?', '')['balances']
    for symbol in symbol_lists:
        for value in balance_list:
            if value['asset'] == cut_usdt(symbol):
                new_balance_list.append(value)
            else:
                pass
    print('new_balance_list')
    print(new_balance_list)


    # BTC price
    btc_price_in_usdt = float(historical_candle['BTCUSDT'][-1][4])
    print('btc_price_in_usdt')
    print(btc_price_in_usdt)

    # # BNB close price
    # bnb_close_price = float(get_latest_candle('BNBUSDT', interval, endTime)[0][4])
    #
    # # BNB balance
    # bnb_balance = float(get_free_balance('BNB'))
    #
    # # BNB auto-buy logic
    # for symbol_info in exchange_info:
    #     if symbol_info['symbol'] == 'BNBUSDT':
    #         print(symbol_info)
    #         bnb_tickSize = float(symbol_info['filters'][0]['tickSize'])
    #         print(bnb_tickSize)
    #         bnb_stepSize = float(symbol_info['filters'][1]['stepSize'])
    #         print(bnb_stepSize)
    #         bnb_minNotional = float(symbol_info['filters'][2]['minNotional'])
    #         print(bnb_minNotional)
    #
    #         if bnb_balance * bnb_close_price < quantity_in_btc * len(symbol_lists) * 0.001:
    #             bnb_quantity = quantity_in_btc * len(symbol_lists) * 0.0005 / bnb_close_price
    #             bnb_quantity = apply_lot_size(bnb_quantity, bnb_stepSize)
    #             print(bnb_quantity)
    #             bnb_price = bnb_close_price * 2
    #             print(bnb_price)
    #             # bnb_price = apply_tick_size(bnb_price, bnb_tickSize)
    #             # print(bnb_price)
    #             if bnb_price * bnb_quantity > bnb_minNotional:
    #                 print('[1]')
    #                 print(buy_limit('BNBUSDT', bnb_quantity, bnb_price))
    #             # elif bnb_price * bnb_quantity < bnb_minNotional and bnb_price > bnb_minNotional:
    #             #     print('[2]')
    #             #     print(buy_limit('BNBUSDT', quantity_in_btc / quantity_in_btc, bnb_price))
    #             else:
    #                 bnb_quantity = bnb_minNotional / bnb_price + 1
    #                 bnb_quantity = apply_lot_size(bnb_quantity, bnb_stepSize)
    #                 print(bnb_quantity)
    #                 print('[3]')
    #                 print(buy_limit('BNBUSDT', bnb_quantity, bnb_price))
    #         else:
    #             print('No need to buy more BNB, yet')
    #             pass
    #
    #     else:
    #         pass



    # trading logic
    for symbol in symbol_lists:
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))

        # # create volume list
        # volume_list = []
        # temp_list = historical_candle[symbol][:-6:-1] # 순서는 거꾸로지만 리스트는 맞다.. 현재 봉 포함한 5개봉의 BTC볼륨 데이터
        # for j in temp_list:
        #     volume_list.append(float(j[7]))
        #
        # # find max_volume
        # max_volume = max(volume_list)

        # create list of close value
        close_value = []
        for i in historical_candle[symbol]:
            close_value.append(float(i[4]))

        # bollinger band
        middle_band = numpy.average(close_value)
        # std_value = numpy.std(close_value)
        # upper_band = middle_band + (k * std_value)
        # lower_band = middle_band - (k * std_value)
        # print(upper_band)
        # print(lower_band)

        print(symbol + ' ' + historical_candle[symbol][-2][4] + ' ' + str(middle_band) + ' ' + historical_candle[symbol][-1][4])

        for symbol_info in exchange_info:

            if symbol_info['symbol'] == symbol:
                print('symbol_info')
                print(symbol_info)
                tickSize = symbol_info['filters'][0]['tickSize'] # price_filter, minPrice
                stepSize = symbol_info['filters'][1]['stepSize'] # lot_size, minQty

                open_orders = get_open_orders(symbol)
                print('open_orders')
                print(open_orders)

                if open_orders is None or len(open_orders) == 0:
                    print('since no open order')
                    # 봇을 재부팅 할 때, 하필 30분봉이 middle_band를 넘어서는 코인이 있다면 거래가 중복될 것이다
                    # 일단은 봇을 29분에 끄고 31분에 켜는 것을 원칙으로 한다

                    # current_candle = historical_candle[symbol][-1]
                    # previous_candle = historical_candle[symbol][-2]

                    # middle_band 상향 돌파 BUY
                    if float(historical_candle[symbol][-2][4]) < middle_band and float(historical_candle[symbol][-1][4]) > middle_band:
                        name = cut_usdt(symbol)
                        print(name)
                        for value in new_balance_list:
                            if value['asset'] == name:
                                current_balance = float(value['free']) + float(value['locked'])
                                if float(historical_candle[symbol][-1][4]) * current_balance < quantity_in_btc * float(historical_candle['BTCUSDT'][-1][4]) * 0.5:
                                    price = apply_tick_size(float(historical_candle[symbol][-1][4]) * (1 + percent_on_price), tickSize)
                                    print(price)
                                    print(stepSize)
                                    quantity = apply_lot_size(get_usdt_quantity_to_buy(float(historical_candle[symbol][-1][4])), stepSize) - float(stepSize)
                                    print(quantity)
                                    print(symbol)
                                    print(buy_limit(symbol, quantity, price))
                                    print(historical_candle[symbol][-2][4] + ' ' + str(middle_band) + ' ' + historical_candle[symbol][-1][4])
                                    print(symbol + ': buy_limit done!')
                                    continue
                                else:
                                    print('already has ' + symbol)
                                    pass
                            else:
                                pass
                    # # 신고 거래량 & 양봉 & middle_band과 lower_band 사이에 있으면 BUY
                    # elif max_volume == float(historical_candle[symbol][-1][7]) and float(historical_candle[symbol][-1][1]) < float(historical_candle[symbol][-1][4]) and float(historical_candle[symbol][-1][4]) < middle_band and float(historical_candle[symbol][-1][4]) > lower_band:
                    #     name = cut_usdt(symbol)
                    #     for value in new_balance_list:
                    #         if value['asset'] == name:
                    #             current_balance = float(value['free']) + float(value['locked'])
                    #             if float(historical_candle[symbol][-1][4]) * current_balance < quantity_in_btc * float(historical_candle['BTCUSDT'][-1][4]) * 0.5:
                    #                 price = apply_tick_size(float(historical_candle[symbol][-1][4]) * (1 + percent_on_price), tickSize)
                    #                 quantity = apply_lot_size(get_usdt_quantity_to_buy(middle_band, btc_price_in_usdt), stepSize)
                    #                 print(buy_limit(symbol, quantity, price))
                    #                 print(symbol + ': buy_limit done!')
                    #                 continue
                    #             else:
                    #                 pass
                    #         else:
                    #             pass
                    # # upper_band 하향 돌파 SELL (high and close)
                    # elif float(historical_candle[symbol][-2][2]) > upper_band and float(historical_candle[symbol][-1][4]) < upper_band:
                    #     print('Price to sell for ' + symbol)
                    #     price = apply_tick_size(float(historical_candle[symbol][-1][4]) * (1 - percent_on_price), tickSize)
                    #     print(sell_limit_all(symbol, price, stepSize))
                    #     print(str(upper_band) + ' ' + historical_candle[symbol][-1][4])
                    #     print(symbol + ': sell_limit done!')
                    #     continue
                    # # upper_band 하향 돌파 SELL (close and close)
                    # elif float(historical_candle[symbol][-2][4]) > upper_band and float(historical_candle[symbol][-1][4]) < upper_band:
                    #     print('Price to sell for ' + symbol)
                    #     price = apply_tick_size(float(historical_candle[symbol][-1][4]) * (1 - percent_on_price), tickSize)
                    #     print(sell_limit_all(symbol, price, stepSize))
                    #     print(str(upper_band) + ' ' + historical_candle[symbol][-1][4])
                    #     print(symbol + ': sell_limit done!')
                    #     continue
                    # middle_band 보다 아래 SELL
                    elif float(historical_candle[symbol][-1][4]) < middle_band:
                        print('Price to sell for ' + symbol)
                        price = apply_tick_size(float(historical_candle[symbol][-1][4]) * (1 - percent_on_price), tickSize)
                        print(str(symbol) + ' ' + str(price) + ' ' + str(stepSize))
                        print(sell_limit_all(symbol, price, stepSize))
                        print(str(middle_band) + ' ' + historical_candle[symbol][-1][4])
                        print(symbol + ': sell_limit done!')
                        continue
                    # # lower_band 보다 아래 SELL
                    # elif float(historical_candle[symbol][-1][4]) < lower_band:
                    #     print('Price to sell for ' + symbol)
                    #     price = apply_tick_size(float(historical_candle[symbol][-1][4]) * (1 - percent_on_price), tickSize)
                    #     print(sell_limit_all(symbol, price, stepSize))
                    #     print(str(lower_band) + ' ' + historical_candle[symbol][-1][4])
                    #     print(symbol + ': sell_limit done!')
                    #     continue
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
