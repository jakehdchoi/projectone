
import time
import requests
# import hashlib
# import hmac
import json
import numpy
import pickle

import config
import symbol_lists

from binance_api import *

# 비트와 이더 시작일: 2017-8-17
simulation_period_list = {
    'day': 86400000,
    'week': 604800000,
    'month': 2592000000
}
simulation_period = simulation_period_list['day'] / 12

initial_amount_in_btc = 10
trade_amount_in_btc = 4



def main():
    print('Starting binancebot simulator...')
    print(time.strftime('start: ' + '%Y-%m-%d %H:%M:%S', time.localtime()))

    print(simulation_period)


    global initial_amount_in_btc
    global simulation_startTime, simulation_endTime
    # simulation_endTime = int(timestamp()) - int(interval_num)
    simulation_endTime = int(1516697115000) - int(interval_num)
    print(simulation_endTime)
    simulation_startTime = int(calculate_simulation_start_time(simulation_endTime, simulation_period))
    print(simulation_startTime)

    simulation_candle_full_list = {}
    for symbol in symbol_lists:
        simulation_candle_full_list[symbol] = get_simulation_data(symbol, interval, simulation_startTime, simulation_endTime)
    print(simulation_candle_full_list['BTCUSDT'])


    with open('BTCUSDT_simulation' + '_' + interval + '_candle.data','r') as mydata:
        a_list = json.load(mydata)

    a_list.append(simulation_candle_full_list['BTCUSDT'])
    with open('BTCUSDT_simulation' + '_' + interval + '_candle.data','w') as mysavedata:
        json.dump(a_list, mysavedata)


    print(a_list)








    # print('json file saved')
    # with open('BTCUSDT_simulation' + '_' + interval + '_candle.data','a+') as mysavedata:
    #     json.dump(simulation_candle_full_list['BTCUSDT'], mysavedata)
    #
    # print('json file open')
    # with open('BTCUSDT_simulation' + '_' + interval + '_candle.data','r') as myloaddata:
    #     a_list = json.load(myloaddata)
    #
    # print(a_list)





    # try:
    #     f = open('BTCUSDT_simulation' + '_' + interval + '_candle.data','a')
    #     # print('print file')
    #     # r = f.read().split()
    #     # print(r)
    #
    #     print(simulation_candle_full_list['BTCUSDT'], file=f)
    # except IOError as err:
    #     print('File Error' + str(err))
    # finally:
    #     f.close()

    print(time.strftime('end: ' + '%Y-%m-%d %H:%M:%S', time.localtime()))



if __name__ == "__main__":
    main()
