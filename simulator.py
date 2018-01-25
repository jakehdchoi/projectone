
import time, datetime
import requests
# import hashlib
# import hmac
import json
import numpy

import config
import symbol_lists

from binance_api import *

# # 비트와 이더 시작일: 2017-8-17
# simulation_period_list = {
#     'day': 86400000,
#     'week': 604800000,
#     'month': 2592000000
# }
# simulation_period = simulation_period_list['month']

initial_amount_in_btc = 10
trade_amount_in_btc = 4


### todo





def main():
    print('Starting binancebot simulator...')
    print(time.strftime('start: ' + '%Y-%m-%d %H:%M:%S', time.localtime()))
    print(
        datetime.datetime.fromtimestamp(
            int("1284101485")
        ).strftime('%Y-%m-%d %H:%M:%S')
    )

    # print(simulation_period)


    global initial_amount_in_btc
    # global simulation_startTime, simulation_endTime
    # simulation_endTime = int(timestamp()) - int(interval_num)
    # simulation_endTime = int(1516697115000) - int(interval_num)
    # simulation_startTime = calculate_simulation_start_time(simulation_endTime, simulation_period)
    #
    # simulation_candle_full_list = {}
    # for symbol in symbol_lists:
    #     simulation_candle_full_list[symbol] = get_simulation_data(symbol, interval, simulation_startTime, simulation_endTime)
    # print(len(simulation_candle_full_list['BTCUSDT']))


    global startTime, endTime
    # endTime = int(timestamp()) - int(interval_num)
    endTime = int(1516697115000) - int(interval_num) # 데이터에서 추출하기
    startTime = calculate_start_time(endTime) # n-time candle * period+@

    # historical_candle = {}
    # for symbol in symbol_lists:
    #     historical_candle[symbol] = get_historical_data(symbol, interval, startTime, endTime)
    # print('historical_candle')
    # print(historical_candle)

    # create balance_list
    new_balance_list = {}
    for symbol in symbol_lists:
        symbol = cut_symbol(symbol)
        if symbol == 'BTC':
            new_balance_list[symbol] = initial_amount_in_btc
        else:
            new_balance_list[symbol] = 0
    new_balance_list['USDT'] = 0
    print('new_balance_list')
    print(new_balance_list)


    # BTC price
    # btc_price_in_usdt = float(historical_candle['BTCUSDT'][-1][4])
    # print('btc_price_in_usdt')
    # print(btc_price_in_usdt)



    # # trading logic
    # for symbol in symbol_lists:
    #
    #     # create list of close value
    #     close_value = []
    #     for i in historical_candle[symbol]:
    #         close_value.append(float(i[4]))
    #
    #     # bollinger band
    #     std_value = numpy.std(close_value)
    #     middle_band = numpy.average(close_value)
    #     upper_band = middle_band + (k * std_value)
    #     lower_band = middle_band - (k * std_value)
    #     # print(upper_band)
    #     # print(lower_band)
    #
    #     print(symbol + ' ' + historical_candle[symbol][-2][4] + ' ' + str(middle_band) + ' ' + historical_candle[symbol][-1][4])
    #
    #
    #     # current_candle = historical_candle[symbol][-1]
    #     # previous_candle = historical_candle[symbol][-2]
    #
    #     # middle_band 상향 돌파 BUY
    #     if float(historical_candle[symbol][-2][4]) < middle_band and float(historical_candle[symbol][-1][4]) > middle_band:
    #         name = cut_usdt(symbol)
    #         print(name)
    #         for value in new_balance_list:
    #             if value['asset'] == name:
    #                 current_balance = float(value['free']) + float(value['locked'])
    #                 if float(historical_candle[symbol][-1][4]) * current_balance < quantity_in_btc * float(historical_candle['BTCUSDT'][-1][4]) * 0.5:
    #                     price = apply_tick_size(float(historical_candle[symbol][-1][4]) * (1 + percent_on_price), tickSize)
    #                     print(price)
    #                     quantity = apply_lot_size(get_usdt_quantity_to_buy(middle_band, btc_price_in_usdt), stepSize)
    #                     print(quantity)
    #                     print(symbol)
    #                     print(buy_limit(symbol, quantity, price))
    #                     print(historical_candle[symbol][-2][4] + ' ' + str(middle_band) + ' ' + historical_candle[symbol][-1][4])
    #                     print(symbol + ': buy_limit done!')
    #                     continue
    #                 else:
    #                     print('already has ' + symbol)
    #                     pass
    #             else:
    #                 pass
    #     # upper_band 하향 돌파 SELL (high and close)
    #     elif float(historical_candle[symbol][-2][2]) > upper_band and float(historical_candle[symbol][-1][4]) < upper_band:
    #         print('Price to sell for ' + symbol)
    #         price = apply_tick_size(float(historical_candle[symbol][-1][4]) * (1 - percent_on_price), tickSize)
    #         print(sell_limit_all(symbol, price, stepSize))
    #         print(str(upper_band) + ' ' + historical_candle[symbol][-1][4])
    #         print(symbol + ': sell_limit done!')
    #         continue
    #     # upper_band 하향 돌파 SELL (close and close)
    #     elif float(historical_candle[symbol][-2][4]) > upper_band and float(historical_candle[symbol][-1][4]) < upper_band:
    #         print('Price to sell for ' + symbol)
    #         price = apply_tick_size(float(historical_candle[symbol][-1][4]) * (1 - percent_on_price), tickSize)
    #         print(sell_limit_all(symbol, price, stepSize))
    #         print(str(upper_band) + ' ' + historical_candle[symbol][-1][4])
    #         print(symbol + ': sell_limit done!')
    #         continue
    #     # middle_band 보다 아래 SELL
    #     elif float(historical_candle[symbol][-1][4]) < middle_band:
    #         print('Price to sell for ' + symbol)
    #         price = apply_tick_size(float(historical_candle[symbol][-1][4]) * (1 - percent_on_price), tickSize)
    #         print(str(symbol) + ' ' + str(price) + ' ' + str(stepSize))
    #         print(sell_limit_all(symbol, price, stepSize))
    #         print(str(middle_band) + ' ' + historical_candle[symbol][-1][4])
    #         print(symbol + ': sell_limit done!')
    #         continue


    print(time.strftime('end: ' + '%Y-%m-%d %H:%M:%S', time.localtime()))



if __name__ == "__main__":
    main()
