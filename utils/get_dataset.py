import pandas as pd
import math
import os.path
import time
from binance.client import Client
from datetime import timedelta, datetime
from dateutil import parser
from tqdm import tqdm_notebook #(Optional, used for progress-bars)
from config import BINANCE

KLINE_INTERVAL_1MINUTE= '1m' # ok!
KLINE_INTERVAL_3MINUTE= '3m'
KLINE_INTERVAL_5MINUTE= '5m' # ok!
KLINE_INTERVAL_15MINUTE= '15m' # ok!
KLINE_INTERVAL_30MINUTE= '30m' # ok!
KLINE_INTERVAL_1HOUR= '1h' # ok!
KLINE_INTERVAL_2HOUR= '2h' # ok!
KLINE_INTERVAL_4HOUR= '4h' # ok!
KLINE_INTERVAL_6HOUR= '6h'
KLINE_INTERVAL_8HOUR= '8h'
KLINE_INTERVAL_12HOUR= '12h'
KLINE_INTERVAL_1DAY= '1d'
KLINE_INTERVAL_3DAY= '3d'
KLINE_INTERVAL_1WEEK= '1w'
KLINE_INTERVAL_1MONTH= '1M'


interval = KLINE_INTERVAL_1MINUTE 


client = Client(BINANCE.get("key"), BINANCE.get("secret"))
# 9 meses aprox
N = 300 
date_N_days_ago = datetime.now() - timedelta(days=N)

#filename = "BTCUSDT-" + interval + ".csv"
filename = "FUTURE-BTC-" + interval + ".csv"
filedirectory = "../dataset/databases/"

print("Empieza a descargar cada " + interval )

#klines = client.get_historical_klines('BTCUSDT', interval, date_N_days_ago.strftime("%d %b %Y %H:%M:%S"))
#klines = client.get_historical_klines('BTCUSDT', interval, date_N_days_ago.strftime("%d %b %Y %H:%M:%S"))
klines = client.futures_historical_klines(
    symbol='BTCUSDT',
    interval=interval,  # can play with this e.g. '1h', '4h', '1w', etc.
    start_str='2022-2-15',
    end_str='2022-4-5'
)

data = pd.DataFrame(klines, columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore' ])
data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
# sort ascending
data.set_index('timestamp', inplace=True)
data.sort_values(by=['timestamp'], inplace=True, ascending=True)
data.to_csv(filedirectory + filename)