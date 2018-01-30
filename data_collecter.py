
import time
import requests
# import hashlib
# import hmac
import json
# import numpy

import config
import symbol_lists

from binance_api import *


# todo
# 빈 파일이 존재하는 상태에서는 에러가 난다


# 비트와 이더 시작일: 2017-8-17
# simulation_period_list = {
#     'day': 86400000,
#     'week': 604800000,
#     'month': 2592000000
# }
# simulation_period = int(simulation_period_list['month'] * 6)
# simulation_period = int(simulation_period_list['day'] / 12)

initial_amount_in_btc = 10
trade_amount_in_btc = 4



def main():
    print('Starting binancebot simulator...')
    print(time.strftime('start: ' + '%Y-%m-%d %H:%M:%S', time.localtime()))

    # print(simulation_period)


    global initial_amount_in_btc
    global simulation_startTime, simulation_endTime
    simulation_endTime = int(timestamp()) - int(interval_num)
    # simulation_endTime = int(1516698000000) - int(interval_num)
    # simulation_endTime = int(1502942400000) + int(simulation_period)
    print(simulation_endTime)
    # simulation_startTime = int(calculate_simulation_start_time(simulation_endTime, simulation_period))
    simulation_startTime = 1502942400000 # startTime for BTCUSDT and ETHUSDT
    print(simulation_startTime)

    # simulation_candle_full_list = {}
    for symbol in symbol_lists:
        print('')
        print(symbol)
        try: # update data
            print('try:')
            with open(symbol + '_' + str(period) + 'p_' + interval + '_candle.data', 'r') as f:
                data = json.load(f)
            # f.close()
            # print(data)
            print(len(data))

            while True:
                simulation_startTime = int(data[-1][0]) + int(interval_num)
                new_data = []
                new_data.extend(get_simulation_data(symbol, interval, interval_num, simulation_startTime))
                print(new_data)

                if new_data is None or len(new_data) == 0:
                    print('Error: Failed to update ' + symbol + ' data')
                    break
                elif len(new_data) == 1:
                    print(symbol + ' data is up-to-date')
                    break
                else:
                    data.extend(new_data)
                    filtered_data = list(unique_by_first_n(11, data))
                    # print('filtered_data')
                    # print(filtered_data)
                    filtered_data.pop()
                    f = open(symbol + '_' + str(period) + 'p_' + interval + '_candle.data', 'w')
                    json.dump(filtered_data, f)
                    print(symbol + ' data is updated')
                    print(len(filtered_data))

        except FileNotFoundError: # create new data
            print('FileNotFoundError:')
            data = []
            while True:
                data.extend(get_simulation_data(symbol, interval, interval_num, simulation_startTime))
                try:
                    if data is None or len(data) == 0:
                        break
                    elif data[-1][0] < simulation_startTime:
                        break
                    else:
                        simulation_startTime += int(interval_num * 500)
                except IndexError:
                    print('IndexError:')
                    # time.sleep(1)
                    # data.extend(get_simulation_data(symbol, interval, interval_num, simulation_startTime))
                    pass

            if data is None or len(data) == 0:
                print('Error: Failed to update ' + symbol + ' data')
                break
            elif len(data) == 1:
                print('len(data) is: ' + str(len(data)))
                print(data)
                break
            else:
                print(len(data))
                filtered_data = list(unique_by_first_n(11, data))
                # print('filtered_data')
                # print(filtered_data)
                filtered_data.pop()
                f = open(symbol + '_' + str(period) + 'p_' + interval + '_candle.data', 'w')
                json.dump(filtered_data, f)
                print(len(filtered_data))
        finally:
            f.close()

    print(time.strftime('end: ' + '%Y-%m-%d %H:%M:%S', time.localtime()))



if __name__ == "__main__":
    main()
