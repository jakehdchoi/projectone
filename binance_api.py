
import time
import requests
import hashlib
import hmac
import json

import config
import symbol_lists


api_key = config.api_key
api_secret = config.api_secret

period = config.period
quantity_in_btc = config.quantity_in_btc # the amount you buy in btc for every buy trade, 0.001 is too small and not working

interval = config.interval_symbol[0]
interval_num = config.interval_symbol[1] # in millisec

symbol_lists = symbol_lists.symbol_lists
percent_on_price = config.percent_on_price

current_candle = {}
recvWindow=10000

k = 2 # bollinger band constant


def apply_lot_size(quantity, stepSize):
    remainder = quantity % float(stepSize)
    return quantity - remainder

def apply_tick_size(price, tickSize):
    remainder = price % float(tickSize)
    return price - remainder

def buy_limit(symbol, quantity, price):
    try:
        url = 'https://www.binance.com/api/v3/order?'
        query = 'symbol=' + symbol + '&side=BUY' + '&type=LIMIT' + '&timeInForce=GTC' + '&quantity=' + format_float(quantity) + '&price=' + format_float(price)
        return signed_request(url, query, type='post')
    except:
        print('Binance error in public request: buy_limit for ' + symbol)
        return 'error'

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

def calculate_simulation_start_time(simulation_endTime, simulation_period):
    return simulation_endTime - simulation_period

def calculate_start_time(endTime):
    return endTime - (interval_num * (period + 10)) # 여유있게 10개 정도 더 받아온 다음에 자르기

def cancel_order(symbol, orderId):
    try:
        url = 'https://www.binance.com/api/v3/order?'
        query = 'symbol=' + symbol + '&orderId=' + str(orderId)
        return signed_request(url, query, type='delete')
    except:
        print('Binance error in private request: cancel_order for ' + symbol)
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

def cut_btc(symbol):
    return symbol.replace('BTC','')

def cut_usdt(symbol):
    return symbol.replace('USDT','')

def find_exchange_info(symbol):
    full_lists = simple_request('https://www.binance.com/api/v1/exchangeInfo')
    a = full_lists['symbols']
    for i in a:
        if i['symbol'] == symbol:
            return i
        else:
            pass

def format_float(f):
    return "%.8f" % f

def get_exchange_info():
    return simple_request('https://www.binance.com/api/v1/exchangeInfo')

def get_free_balance(symbol):
    try:
        url = 'https://www.binance.com/api/v3/account?'
        query = ''
        name = cut_usdt(symbol)
        balance_list = signed_request(url, query)['balances']
        for value in balance_list:
            if value['asset'] == name:
                return value['free']
            else:
                pass
    except:
        print('Binance error in public request: get_free_balance for ' + symbol)
        return 'error'

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

def get_latest_candle(symbol, interval, endTime):
    try:
        startTime = endTime - interval_num
        latest_candle = simple_request('https://www.binance.com/api/v1/klines?symbol=' + symbol + '&interval=' + interval + '&startTime=' + str(startTime) + '&endTime=' + str(endTime))
        return latest_candle
    except:
        print('Binance error in public request: get_latest_candle for ' + symbol)
        return 'error'

def get_open_orders(symbol):
    try:
        url = 'https://www.binance.com/api/v3/openOrders?'
        query = 'symbol=' + symbol
        return signed_request(url, query)
    except:
        print('Binance error in private request: get_open_orders for ' + symbol)
        return 'error'

def get_simulation_data(symbol, interval, startTime, endTime):
    try:
        return simple_request('https://www.binance.com/api/v1/klines?symbol=' + symbol + '&interval=' + interval + '&startTime=' + str(startTime) + '&endTime=' + str(endTime))
    except:
        print('Binance error in public request: klines for ' + symbol)
        return 'error'

def get_quantity_to_buy(price):
    return quantity_in_btc / price

def get_usdt_quantity_to_buy(target_price_in_usdt, btc_price_in_usdt):
    return quantity_in_btc * btc_price_in_usdt / target_price_in_usdt

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

def recursive_request(url):
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()
    else:
        return recursive_request(url)

def sell_limit(symbol, quantity, price):
    try:
        if quantity == 0:
            return print('nothing to sell')
        else:
            url = 'https://www.binance.com/api/v3/order?'
            query = 'symbol=' + symbol + '&side=SELL' + '&type=LIMIT' + '&timeInForce=GTC' + '&quantity=' + format_float(quantity) + '&price=' + format_float(price)
            return signed_request(url, query, type='post')
    except:
        print('Binance error in public request: sell_limit for ' + symbol)
        return 'error'

def sell_limit_all(symbol, price, stepSize):
    try:
        balance = apply_lot_size(float(get_free_balance(symbol)), stepSize)
        return sell_limit(symbol, balance, price)
    except:
        print('Binance error in public request: sell_limit_all for ' + symbol)
        return 'error'

def signed_request(url, query, type='get'):
    try:
        query += '&recvWindow=' + str(recvWindow) + '&timestamp=' + str(timestamp())
        signature = hmac.new((api_secret).encode('utf-8'), query.encode('utf-8'), hashlib.sha256).hexdigest()
        headers = {'X-MBX-APIKEY': api_key}

        if type == 'get':
            r = requests.get(url + query + '&signature=' + signature, headers=headers)
            if r.status_code == 200:
                return r.json()
            else:
                return signed_request_again(url, query)
        if type == 'post':
            r = requests.post(url + query + '&signature=' + signature, headers=headers)
            if r.status_code == 200:
                return r.json()
            else:
                return signed_request_again(url, query, type='post')
        if type =='delete':
            r = requests.delete(url + query + '&signature=' + signature, headers=headers)
            if r.status_code == 200:
                return r.json()
            else:
                return signed_request_again(url, query, type='delete')
    except:
        print('Binance error in public request: signed_request')
        return 'error'

def signed_request_again(url, query, type='get'):
    try:
        time.sleep(0.5)
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
    if r.status_code == 200:
        return r.json()
    else:
        return simple_request_again(url)

def simple_request_again(url):
    time.sleep(0.5)
    r = requests.get(url)
    return r.json()

def timestamp():
    try:
        timestamp = simple_request('https://www.binance.com/api/v1/time?')
        if timestamp is None or len(timestamp) == 0:
            return timestamp()
        else:
            return timestamp['serverTime']
    except:
        print('Binance error in public request: timestamp')
        return 'error'
