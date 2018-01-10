
import time
import requests
import hashlib
import hmac
import json

import config
import symbol_lists

### note
# crontab version

### todo
# get_open_orders()를 반복할 필요 없음
# apply_lot_size()를 반복할 필요 없음
# test 구현
## 시간대별로 현재 자산가치(BTC)를 파일에 기록하는 로직이 필요
# api 동작이 실패하면 다시 시도하는 로직 필요 (모든 함수에 대해서)


api_key = config.api_key
api_secret = config.api_secret

period = config.period
quantity_in_btc = config.quantity_in_btc # the amount you buy in btc for every buy trade, 0.001 is too small and not working

interval = config.interval
interval_num = config.interval_num
interval_lists = config.interval_lists

symbol_lists = symbol_lists.symbol_lists

current_candle = {}
recvWindow=10000 # 10 sec


def main():
    print('Starting binancebot...')
    time.sleep(10)
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))

    global endTime, startTime
    endTime = int(timestamp()) - int(interval_num)
    startTime = calculate_start_time(endTime) # n-time candle 81+개에대한 시작시간

    # symbol이 이미 존재한다면 pass 하는 로직 구현 필요
    for symbol in symbol_lists:
        current_candle[symbol] = []
    # print(current_candle)

    # 현재 balance를 볼 수 있는 로직
    # for symbol in symbol_lists:
    #     # 밸런스를 받아오지 못 하는 경우는 어떻게 처리해야 하지.. 재시도 로직?
    #     print(get_total_balance(symbol))

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


def timestamp():
    try:
        timestamp = simple_request('https://www.binance.com/api/v1/time?')
        return timestamp['serverTime']
    except:
        print('Binance error in public request: timestamp')
        return 'error'

def get_exchange_info():
    return simple_request('https://www.binance.com/api/v1/exchangeInfo')

def find_exchange_info(symbol):
    full_lists = simple_request('https://www.binance.com/api/v1/exchangeInfo')
    a = full_lists['symbols']
    for i in a:
        if i['symbol'] == symbol:
            return i
        else:
            pass

def apply_lot_size(symbol, quantity):
    step_size = find_exchange_info(symbol)['filters'][1]['stepSize']
    remainder = quantity % float(step_size)
    return quantity - remainder

def get_latest_candle(symbol, interval, endTime):
    try:
        startTime = endTime - interval_num
        latest_candle = simple_request('https://www.binance.com/api/v1/klines?symbol=' + symbol + '&interval=' + interval + '&startTime=' + str(startTime) + '&endTime=' + str(endTime))
        return latest_candle
    except:
        print('Binance error in public request: get_latest_candle for ' + symbol)
        return 'error'

def check_latest_candle_update(symbol, interval, endTime):
    try:
        global current_candle, latest_candle
        latest_candle = get_latest_candle(symbol, interval, endTime)
        if current_candle[symbol] != latest_candle:
            if latest_candle is None or len(latest_candle) == 0:
                return False
            else:
                current_candle[symbol] = latest_candle
                return True
        else:
            return False
    except:
        print('Binance error in public request: check_latest_candle_update for ' + symbol)
        return 'error'

def calculate_start_time(endTime):
    return endTime - (interval_num * (period + 10)) # 여유있게 10개 정도 더 받아온 다음에 자르기

def get_historical_data(symbol, interval, startTime, endTime):
    try:
        historical_data = simple_request('https://www.binance.com/api/v1/klines?symbol=' + symbol + '&interval=' + interval + '&startTime=' + str(startTime) + '&endTime=' + str(endTime))
        return historical_data[-period:]
    except:
        print('Binance error in public request: klines for ' + symbol)
        return 'error'
        # [
        #   [
        #     1499040000000,      // [0] Open time
        #     "0.01634790",       // [1] Open
        #     "0.80000000",       // [2] High
        #     "0.01575800",       // [3] Low
        #     "0.01577100",       // [4] Close
        #     "148976.11427815",  // [5] Volume
        #     1499644799999,      // [6] Close time
        #     "2434.19055334",    // [7] Quote asset volume 'BTC Volume'
        #     308,                // [8] Number of trades
        #     "1756.87402397",    // [9] Taker buy base asset volume
        #     "28.46694368",      // [10] Taker buy quote asset volume
        #     "17928899.62484339" // [11] Can be ignored
        #   ], ... []
        # ]

def calculate_sma(symbol, interval, startTime, endTime, period):
    try:
        historical_data = get_historical_data(symbol, interval, startTime, endTime)
        total_closing = 0

        for i in range(0, period):
            total_closing = float(historical_data[i][4]) + total_closing
        return total_closing / period
    except:
        print('Binance error in public request: calculate_sma for ' + symbol)
        return 'error'

def cut_btc(symbol):
    return symbol.replace('BTC','')

def get_total_balance(symbol):
    try:
        url = 'https://www.binance.com/api/v3/account?'
        query = ''
        name = cut_btc(symbol)
        balance_list = signed_request(url, query)['balances']
        for value in balance_list:
            if value['asset'] == name:
                return value
            else:
                pass
    except:
        print('Binance error in public request: get_total_balance for ' + symbol)
        return 'error'

def get_free_balance(symbol):
    try:
        url = 'https://www.binance.com/api/v3/account?'
        query = ''
        name = cut_btc(symbol)
        balance_list = signed_request(url, query)['balances']
        for value in balance_list:
            if value['asset'] == name:
                return value['free']
            else:
                pass
    except:
        print('Binance error in public request: get_free_balance for ' + symbol)
        return 'error'

def sell_limit(symbol, quantity, price):
    try:
        if quantity == 0:
            return print('nothing to sell')
        else:
            quantity = apply_lot_size(symbol, quantity)
            url = 'https://www.binance.com/api/v3/order?'
            query = 'symbol=' + symbol + '&side=SELL' + '&type=LIMIT' + '&timeInForce=GTC' + '&quantity=' + format_float(quantity) + '&price=' + format_float(price)
            return signed_request(url, query, type='post')
    except:
        print('Binance error in public request: sell_limit for ' + symbol)
        return 'error'

def sell_limit_all(symbol, price):
    try:
        balance = float(get_free_balance(symbol))
        return sell_limit(symbol, balance, price)
    except:
        print('Binance error in public request: sell_limit_all for ' + symbol)
        return 'error'

def get_quantity_to_buy(rate):
    return quantity_in_btc / rate

def buy_limit(symbol, quantity, price):
    try:
        quantity = apply_lot_size(symbol, quantity)
        url = 'https://www.binance.com/api/v3/order?'
        query = 'symbol=' + symbol + '&side=BUY' + '&type=LIMIT' + '&timeInForce=GTC' + '&quantity=' + format_float(quantity) + '&price=' + format_float(price)
        return signed_request(url, query, type='post')
    except:
        print('Binance error in public request: buy_limit for ' + symbol)
        return 'error'

def get_open_orders(symbol):
    try:
        url = 'https://www.binance.com/api/v3/openOrders?'
        query = 'symbol=' + symbol
        return signed_request(url, query)
    except:
        print('Binance error in private request: get_open_orders for ' + symbol)
        return 'error'

def cancel_order(symbol, orderId):
    try:
        url = 'https://www.binance.com/api/v3/order?'
        query = 'symbol=' + symbol + '&orderId=' + str(orderId)
        return signed_request(url, query, type='delete')
    except:
        print('Binance error in private request: cancel_order for ' + symbol)
        return 'error'

def signed_request(url, query, type='get'):
    try:
        query += '&recvWindow=' + str(recvWindow) + '&timestamp=' + str(timestamp())
        signature = hmac.new((api_secret).encode('utf-8'), query.encode('utf-8'), hashlib.sha256).hexdigest()
        headers = {'X-MBX-APIKEY': api_key}

        if type == 'get':
            r = requests.get(url + query + '&signature=' + signature, headers=headers)
            return r.json()
        if type == 'post':
            r = requests.post(url + query + '&signature=' + signature, headers=headers)
            return r.json()
        if type =='delete':
            r = requests.delete(url + query + '&signature=' + signature, headers=headers)
            return r.json()
    except:
        print('Binance error in public request: signed_request')
        return 'error'

def simple_request(url):
    r = requests.get(url)
    return r.json()

def format_float(f):
    return "%.8f" % f


if __name__ == "__main__":
    main()
