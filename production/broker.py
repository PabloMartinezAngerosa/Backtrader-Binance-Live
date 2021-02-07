from binance.client import Client
from binance.enums import *
import websocket, json, pprint, talib, numpy
from config import BINANCE, COIN_REFER, COIN_TARGET
from datetime import timedelta, datetime
import pandas as pd
import math

class BrokerProduction:
    def __init__(self, info, interval="KLINE_INTERVAL_1MINUTE"):
        self.comminfo = info
        self.interval = {
            'KLINE_INTERVAL_1MINUTE': '1m',
            'KLINE_INTERVAL_3MINUTE': '3m',
            'KLINE_INTERVAL_5MINUTE': '5m',
            'KLINE_INTERVAL_15MINUTE': '15m',
            'KLINE_INTERVAL_30MINUTE': '30m',
            'KLINE_INTERVAL_1HOUR': '1h',
            'KLINE_INTERVAL_2HOUR': '2h',
            'KLINE_INTERVAL_4HOUR': '4h',
            'KLINE_INTERVAL_6HOUR': '6h',
            'KLINE_INTERVAL_8HOUR': '8h',
            'KLINE_INTERVAL_12HOUR': '12h',
            'KLINE_INTERVAL_1DAY': '1d',
            'KLINE_INTERVAL_3DAY': '3d',
            'KLINE_INTERVAL_1WEEK': '1w',
            'KLINE_INTERVAL_1MONTH': '1M'
        }
        self.klineInterval = interval
        self.cerebro = None
        self.socket  = "wss://stream.binance.com:9443/ws/btcusdt@kline_" + self.interval[self.klineInterval]
        self.symbol = COIN_TARGET + COIN_REFER 
        self.client = Client(BINANCE.get("key"), BINANCE.get("secret"))

    def run(self):
        self.ws = websocket.WebSocketApp(self.socket,
                    on_message = lambda ws,msg: self.on_message(ws, msg),
                    on_error   = lambda ws,msg: self.on_error(ws, msg),
                    on_close   = lambda ws:     self.on_close(ws),
                    on_open    = lambda ws:     self.on_open(ws))
        self.ws.run_forever()

    def set_cerebro(self,cerebro):
        self.cerebro = cerebro
    
    def on_open(self,ws):
        print("opened connection")

    def on_close(self,ws):
        print("closed connection")

    def on_message(self,ws, message):
        json_message = json.loads(message)
        
        candle = json_message["k"]
        is_candle_closed = candle["x"]
        timestamp = pd.to_datetime(candle['T'], unit='ms')

        close = candle["c"]
        open = candle["o"]
        low = candle["l"]
        high = candle["h"]
        volume = candle["v"] 

        self.cerebro.addNextFrame(0,timestamp, open, low, high, close, volume)
        if (is_candle_closed):
            print(message)
            self.cerebro.addNextFrame(1, timestamp, open,  low, high, close, volume)

    def on_error(self, ws, message):
        print("Error socket")
        print(message)
        # self.run()
    
    def get_historical_klines(self, interval="KLINE_INTERVAL_1MINUTE", lapse=1):
        print("Getting last 1 days")
        N = lapse
        date_N_days_ago = datetime.now() - timedelta(days=N) 
        klines = self.client.get_historical_klines(self.symbol, self.interval[interval], date_N_days_ago.strftime("%d %b %Y %H:%M:%S"))
        data = pd.DataFrame(klines, columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore' ])
        data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
        
        data.set_index('timestamp', inplace=True)
        data.sort_values(by=['timestamp'], inplace=True, ascending=True)

        row = len(data.index)
        for i in range(row):
            datatime = data.index[i]    
            open = data.iat[i,0]
            high = data.iat[i,1]
            low = data.iat[i,2]
            close = data.iat[i,3]
            volume = data.iat[i,4]
            self.cerebro.addNextFrame(1,datatime, open, low, high, close, volume,  False)
        self.cerebro.setLenData1()