import sqlalchemy as sql
from sqlalchemy.orm import Session
from config import SQL,  DEVELOPMENT, ENV, PRODUCTION,DEBUG
import pandas as pd
import os.path



# singleton class
class SqlCache:
    __instance = None
    @staticmethod 
    def getInstance():
        """ Static access method. """
        if SqlCache.__instance == None:
            SqlCache()
        return SqlCache.__instance
    
    def __init__(self):
        """ Virtually private constructor. """
        if SqlCache.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            SqlCache.__instance = self
        self.engine = sql.create_engine("mysql+mysqlconnector://" +   SQL.get("user") + ":" + SQL.get("pass")  + "@localhost/binance")
        self.metadata = sql.MetaData()
        self.connection = self.engine.connect()
        self.table_combo_estimations = sql.Table('combo_estimations', self.metadata, autoload=True, autoload_with=self.engine)
        self.table_realtime_price_miliseconds = sql.Table("realtime_price_miliseconds", self.metadata, autoload=True, autoload_with=self.engine)


    def check_estimators(self, date, candle, lags, length_frames, coin="BTC"):
        query = sql.select([self.table_combo_estimations]).where(sql.and_(
            self.table_combo_estimations.columns.date  == date, 
            self.table_combo_estimations.columns.candle_min  == candle,
            self.table_combo_estimations.columns.lags  == lags,
            self.table_combo_estimations.columns.coin == coin,
            self.table_combo_estimations.columns.length_frames == length_frames))
        result = self.connection.execute(query)
        #print(result)
        return result


    def insert_realtime_price(self, date, open, low, high, close, volume, datetime_closed, is_candle_closed, coin = "BTC"):
        query = sql.insert(self.table_realtime_price_miliseconds).values(
            open = open,
            low = low,
            close = close,
            high = high,
            volume = volume,
            timestamp = date,
            timestamp_close = datetime_closed,
            is_close = is_candle_closed,
            coin = coin
        )
        result_proxy = self.connection.execute(query)
    
    def insert_realtime_price_with_phemex(self, date, open, low, high, close, volume, datetime_closed, is_candle_closed, phemex_price):
        query = sql.insert(self.table_realtime_price_miliseconds).values(
            open = open,
            low = low,
            close = close,
            high = high,
            volume = volume,
            timestamp = date,
            timestamp_close = datetime_closed,
            is_close = is_candle_closed,
            phemex_close = phemex_price
        )
        result_proxy = self.connection.execute(query)

    def insert_estimators(self, date, candle_min, lags, length_frames, estimations, coin="BTC"):

        # low values
        low_mean = estimations.mediaEstimadorLow
        low_mean2 = estimations.mediaEstimadorLow_iterada2
        low_mean3 = estimations.mediaEstimadorLow_iterada3
        low_delta = estimations.deltaMediaOpenLow
        low_combo = estimations.lowCombo
        # high values
        high_mean = estimations.mediaEstimadorHigh
        high_mean2 = estimations.mediaEstimadorHigh_iterada2
        high_mean3 = estimations.mediaEstimadorHigh_iterada3
        high_delta = estimations.deltaMediaOpenHigh
        high_combo = estimations.highCombo

        close_mean = estimations.mediaEstimadorClose
        close_combo = estimations.closeCombo

        query = sql.insert(self.table_combo_estimations).values(date=date, candle_min=candle_min, lags=lags, length_frames = length_frames,
                           low_mean=low_mean, low_mean2 = low_mean2, low_mean3 = low_mean3, low_delta = low_delta, low_combo = low_combo,
                           high_mean = high_mean, high_mean2=high_mean2, high_mean3=high_mean3, high_delta= high_delta, high_combo = high_combo,
                           close_mean=close_mean, close_combo = close_combo, coin = coin) 
        result_proxy = self.connection.execute(query)

    def create_real_time_price_csv(self, _from, _to):
        # select from to values
        print("Start select")

        query = sql.select([self.table_realtime_price_miliseconds]).where(sql.and_(
            self.table_realtime_price_miliseconds.columns.timestamp  >= _from, 
            self.table_realtime_price_miliseconds.columns.timestamp  <= _to))
        # result = self.connection.execute(query)


        interval = "milliseconds_"  + str(_from) + "_" + str(_to) 
        filename = "BTCUSDT-" + interval + ".csv"
        filedirectory = "./dataset/databases/"
        data = pd.read_sql(query, self.connection)
        column_names = ["timestamp", "open", "high", "low", "close", "volume"]
        data = data.reindex(columns=column_names)
        data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
        # backtrader ejecuta una orden con el proximo open para simular demora
        # se reescribe los open con los close. Xq no existe esa infromacion.
        data['open'] = data['close']
        # sort ascending
        data.set_index('timestamp', inplace=True)
        data.sort_values(by=['timestamp'], inplace=True, ascending=True)
        data.to_csv(filedirectory + filename)

    def get_ticks_realtime(self, _from, _to):
        query = sql.select([self.table_realtime_price_miliseconds]).where(sql.and_(
            self.table_realtime_price_miliseconds.columns.timestamp  >= _from, 
            self.table_realtime_price_miliseconds.columns.timestamp  <= _to))
        data = pd.read_sql(query, self.connection)
        return data