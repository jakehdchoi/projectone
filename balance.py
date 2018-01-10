
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
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))

    global endTime, startTime
    endTime = int(timestamp()) - int(interval_num)
    startTime = calculate_start_time(endTime) # n-time candle 81+개에대한 시작시간

    for symbol in symbol_lists:
        current_candle[symbol] = []
    # print(current_candle)

    # 현재 balance를 볼 수 있는 로직
    for symbol in symbol_lists:
        # 밸런스를 받아오지 못 하는 경우는 어떻게 처리해야 하지.. 재시도 로직?
        print(get_total_balance(symbol))


    # account = signed_request('https://www.binance.com/api/v3/account?', '')
    # print('')
    # print(account)


if __name__ == "__main__":
    main()
