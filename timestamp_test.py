
import time
import requests
import json


# timestamp 실패하면 다시 시도하는 로직 구현


def main():
    while True:
        time.sleep(0.1)
        timestamp = simple_request('https://www.binance.com/api/v1/time?')
        # print(timestamp)

        try:
            f = open('time.csv','a')
            print(timestamp, file=f)

        except IOError as err:
            print('File Error' + str(err))
            print('File Error', file=f)
            print(timestamp, file=f)
        finally:
            f.close()








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
