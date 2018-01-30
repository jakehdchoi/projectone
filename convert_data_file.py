
import time, datetime
import json

import config
from binance_api import *


### todo
# 파일에 트레이딩 횟수 같이 저장



def main():
    print('Starting binancebot simulator...')
    print(time.strftime('start: ' + '%Y-%m-%d %H:%M:%S', time.localtime()))
    print(
        datetime.datetime.fromtimestamp(
            int("1284101485")
        ).strftime('%Y-%m-%d %H:%M:%S')
    )


    symbol = 'BTCUSDT'

    print('')
    try: # 파일이 없으면 예외 발생
        print('try: ' + symbol)
        with open(symbol + '_' + str(period) + 'p_' + interval + '_candle.data', 'r') as f:
            data = json.load(f)
        print(len(data))

        for i in data:
            # print & write
            with open(symbol + '_' + str(period) + 'p_' + interval + '_converted_data.txt', 'a') as f:
                r = datetime.datetime.fromtimestamp(int(i[0]) / 1000).strftime('%Y-%m-%d %H:%M:%S' + ',')
                rclosed = float(i[4])
                f.write(r)
                f.write(str(rclosed))
                f.write('\n')

    except FileNotFoundError:
        print('FileNotFoundError: ' + symbol)
        pass





    # print(new_balance_list)
    print('')
    print(time.strftime('end: ' + '%Y-%m-%d %H:%M:%S', time.localtime()))



if __name__ == "__main__":
    main()
