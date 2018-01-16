
import time
import requests
import hashlib
import hmac
import json

import config

api_key = config.api_key
api_secret = config.api_secret

recvWindow=10000


def main():
    while True:
        time.sleep(1)
        # timestamp = simple_request('https://www.binance.com/api/v1/time?')
        # print(timestamp)

        print(get_total_balance('BNBBTC'))

        # try:
        #     f = open('time.csv','a')
        #     print(timestamp, file=f)
        #
        # except IOError as err:
        #     print('File Error' + str(err))
        #     print('File Error', file=f)
        #     print(timestamp, file=f)
        # finally:
        #     f.close()



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

def signed_request(url, query, type='get'):
    try:
        query_copy = query
        query += '&recvWindow=' + str(recvWindow) + '&timestamp=' + str(timestamp())
        signature = hmac.new((api_secret).encode('utf-8'), query.encode('utf-8'), hashlib.sha256).hexdigest()
        headers = {'X-MBX-APIKEY': api_key}

        if type == 'get':
            r = requests.get(url + query + '&signature=' + signature, headers=headers)
            if r.status_code == 200:
                return r.json()
            else:
                return signed_request(url, query_copy)
        if type == 'post':
            r = requests.post(url + query + '&signature=' + signature, headers=headers)
            return r.json()
        if type =='delete':
            r = requests.delete(url + query + '&signature=' + signature, headers=headers)
            return r.json()
    except:
        print('Binance error in public request: signed_request')
        return 'error'

def timestamp():
    try:
        timestamp = simple_request('https://www.binance.com/api/v1/time?')
        return timestamp['serverTime']
    except:
        print('Binance error in public request: timestamp')
        return 'error'

def simple_request(url):
    r = requests.get(url)
    return r.json()


if __name__ == "__main__":
    main()
