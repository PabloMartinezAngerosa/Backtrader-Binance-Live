from binance.client import Client
from binance.enums import *
import websocket, json, pprint, numpy
from config import BINANCE, COIN_REFER, COIN_TARGET, PERSISTENCE_CONNECTION, TESTING_PRODUCTION,PHEMEX_PRICE
from datetime import timedelta, datetime
import pandas as pd
import math
from indicators.sqlCache import  SqlCache
from production.automation_phemex import Automation

class BrokerProduction:
    def __init__(self, info, interval, phemex_automation, testing_production_date = None, stand_alone = False):
        self.comminfo = info
        self.testing_production_date = testing_production_date
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
        self.STANDALONE = stand_alone
        self.klineInterval = interval
        self.cerebro = None
        # sin futuros wss://stream.binance.com:9443/ws/btcusdt@kline_
        # con fuures wss://fstream.binance.com/ws/btcusdt@kline_
        self.socket  = "wss://fstream.binance.com/ws/btcusdt@kline_" + self.interval[self.klineInterval]
        print(self.socket)
        self.symbol = COIN_TARGET + COIN_REFER
        # en la version stand alone, en fuerza bruto por ejemplo, no es necesario instanciar el Client.
        # ya hay uno funcionando si es en Live Production o se trate todo lo necesario de la BD. 
        if self.STANDALONE == False: 
            self.client = Client(BINANCE.get("key"), BINANCE.get("secret"))
        try:
            self.sql_cache = SqlCache()
        except:
            self.sql_cache = SqlCache.getInstance()
        # automation phemex
        self.phemex_automation = phemex_automation

    def run(self):
        if TESTING_PRODUCTION == False:
            self.ws = websocket.WebSocketApp(self.socket,
                        on_message = lambda ws,msg: self.on_message(ws, msg),
                        on_error   = lambda ws,msg: self.on_error(ws, msg),
                        on_close   = lambda ws:     self.on_close(ws),
                        on_open    = lambda ws:     self.on_open(ws))
            self.ws.run_forever()
        else:
            self.simulate_binance_socket()
    
    def simulate_binance_socket(self, data_tick= None):
        if self.STANDALONE == False:
            data_tick = self.sql_cache.get_ticks_realtime(self.testing_production_date.get("from"), self.testing_production_date.get("to"))
        # obtiene con datos del config los ticks correspondientes
        for index, tick in data_tick.iterrows():
            message = {}
            candle = {}
            message["E"] = tick["timestamp"]
            candle["x"] = tick["is_close"]
            candle["c"] = tick["close"]
            candle["o"] = tick["open"]
            candle["h"] = tick["high"]
            candle["l"] = tick["low"]
            candle["v"] = tick["volume"]
            candle["T"] = tick["timestamp_close"]
            message["k"] = candle
            message["phemex"] = tick["phemex_close"]
            self.on_message(None, json.dumps(message))
        
        print("Finaliza con los siguientes resultados:")
        print(self.cerebro.get_wallet_balance())
        print("History Balance:")
        print(self.cerebro.get_history_balance())
        print("History Profit por hora")
        print(self.cerebro.get_history_profit())
        print("Binance profit")
        print(self.cerebro.get_binance_wallet_balance())
        print("Binance Leverage")
        print(self.cerebro.get_wallet_balance_leverage())
        # print(self.cerebro.get_wallet_balance_leverage())
        # genera el json_message simulando lo que envia Binance desde el API
        # llama on_message 

    def set_cerebro(self,cerebro):
        self.cerebro = cerebro
    
    def on_open(self,ws):
        print("opened connection")

    def on_close(self,ws):
        print("closed connection")

    def on_message(self,ws, message):
        json_message = json.loads(message)
        # los ticks cuando se dispara el evento
        datetime = json_message['E']
        candle = json_message["k"]
        is_candle_closed = candle["x"]
        timestamp = pd.to_datetime(json_message['E'], unit='ms')

        close = candle["c"]
        open = candle["o"]
        low = candle["l"]
        high = candle["h"]
        volume = candle["v"] 

        datetime_closed = datetime
        is_closed = 0
        print(close)
        if (is_candle_closed):
            is_closed = 1
            # close candle time 
            datetime_closed = candle["T"]
            # no ejecuta next frame
            self.cerebro.addNextFrame(1, datetime, open,  low, high, close, volume, False)
        
        # si esta en config PHEMEX_PRICE
        if PHEMEX_PRICE == True:
            if TESTING_PRODUCTION == True:
                phemex_price = json_message['phemex']
            else:
                phemex_price = self.phemex_automation.get_current_price()
            # addNextFrame con indice 2  en close los demas 0, False
            self.cerebro.addNextFrame(2,datetime, 0, 0, 0, phemex_price, 0, False)    

        self.cerebro.addNextFrame(0,datetime, open, low, high, close, volume, True)
        # agrega el precio realtime a la BD
        # esto solo se llama en ENV = PRODUCTION
        # si hay problema en la BD evita que se corte el flujo del bot.
        #try:
        if TESTING_PRODUCTION == False and self.STANDALONE == False:
            if PHEMEX_PRICE == True:
                # agrega el price pero con el precio phemex
                self.sql_cache.insert_realtime_price_with_phemex(datetime, open, low, high, close, volume, datetime_closed,  is_closed, phemex_price)
            else:
                self.sql_cache.insert_realtime_price(datetime, open, low, high, close, volume, datetime_closed,  is_closed)
        #except:
        #    print("Problema en guardar en la BD el tick en realtime.")

    def on_error(self, ws, message):
        print("Error socket")
        print(message)
        if PERSISTENCE_CONNECTION:
            self.run()
    
    def get_historical_klines(self, interval, lapse):
        print("Getting historical " + self.interval[interval])
        N = lapse
        date_N_days_ago = datetime.now() - timedelta(days=N) 
        klines = self.client.get_historical_klines(self.symbol, self.interval[interval], date_N_days_ago.strftime("%d %b %Y %H:%M:%S"))
        data = pd.DataFrame(klines, columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore' ])
        # data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
        
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

    def order(self, side, quantity, symbol,  order_type = ORDER_TYPE_MARKET):
        try:
            order = self.client.create_order(
                symbol=symbol,
                side=side,
                type=order_type,
                quantity=quantity
            )
        except Exception as e:
            print(e)
            return False
        return True