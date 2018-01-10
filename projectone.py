
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
# get_open_orders()를 반복할 필요 없음
# apply_lot_size()를 반복할 필요 없음
# test 구현
# api 동작이 실패하면 다시 시도하는 로직 필요 (모든 함수에 대해서)
# git clone하면 파이에서 모드변경 없이 동작하는지 확인 (chmod +x *.py)
# 이전봉 close 값과 비교하는 로직으로 변경


def main():
    print('Starting binancebot...')
    time.sleep(10)
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))

    global endTime, startTime
    endTime = int(timestamp()) - int(interval_num)
    startTime = calculate_start_time(endTime) # n-time candle 81+개에대한 시작시간

    for symbol in symbol_lists:
        current_candle[symbol] = []
    # print(current_candle)

    for symbol in symbol_lists:
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
        check_latest_candle_update(symbol, interval, endTime)
        open_orders = get_open_orders(symbol)

        if open_orders is None or len(open_orders) == 0:
            pass
        else:
            cancel_order(symbol, open_orders[0]['orderId'])
            if open_orders[0]['side'] == 'BUY':
                amount = float(open_orders[0]['origQty']) - float(open_orders[0]['executedQty'])
                rate = float(current_candle[symbol][0][4]) * 1.1
                print(buy_limit(symbol, amount, rate))
                print(symbol + ': buy_limit x1.1 done!')
            elif open_orders[0]['side'] == 'SELL':
                amount = float(open_orders[0]['origQty']) - float(open_orders[0]['executedQty'])
                rate = float(current_candle[symbol][0][4]) * 0.9
                print(sell_limit(symbol, amount, rate))
                print(symbol + ': sell_limit x0.9 done!')
            else:
                pass

        # 봇을 재부팅하면 당연히 TRUE가 되는데, 그 때 하필 30분봉이 SMA를 넘어서는 코인이 있다면 거래가 중복될 것이다
        # 일단은 봇을 29분에 끄고 31분에 켜는 것을 원칙으로 한다
        sma = calculate_sma(symbol, interval, startTime, endTime, period)
        # 이전봉 close 값과 비교하는게 더 좋겠다
        if float(current_candle[symbol][0][1]) < sma and float(current_candle[symbol][0][4]) > sma:
            print(buy_limit(symbol, get_quantity_to_buy(sma), float(current_candle[symbol][0][4])))
            print(symbol + ': buy_limit done!')
        elif float(current_candle[symbol][0][4]) < sma:
            print(sell_limit_all(symbol, float(current_candle[symbol][0][4])))
            print(symbol + ': sell_limit done!')
        else:
            pass



if __name__ == "__main__":
    main()
