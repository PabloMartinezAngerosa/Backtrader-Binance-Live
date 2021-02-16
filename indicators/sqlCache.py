import sqlalchemy as sql
from sqlalchemy.orm import Session
from config import SQL

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


    def check_estimators(self, date, candle, lags, length_frames):
        query = sql.select([self.table_combo_estimations]).where(sql.and_(
            self.table_combo_estimations.columns.date  == date, 
            self.table_combo_estimations.columns.candle_min  == candle,
            self.table_combo_estimations.columns.lags  == lags,
            self.table_combo_estimations.columns.length_frames == length_frames))
        result = self.connection.execute(query)
        return result


    def insert_realtime_price(self, date, open, low, high, close, volume):
        query = sql.insert(self.table_realtime_price_miliseconds).values(
            date = date,
            open = open,
            low = low,
            close = close,
            high = high,
            volume = volume
        )
        result_proxy = self.connection.execute(query)

    def insert_estimators(self, date, candle_min, lags, length_frames, estimations):
        # low values
        low_mean = estimations.mediaEstimadorLow
        low_mean2 = estimations.mediaEstimadorLow_iterada2
        low_mean3 = estimations.mediaEstimadorLow_iterada3
        low_delta = estimations.deltaMediaOpenLow
        # high values
        high_mean = estimations.mediaEstimadorHigh
        high_mean2 = estimations.mediaEstimadorHigh_iterada2
        high_mean3 = estimations.mediaEstimadorHigh_iterada3
        high_delta = estimations.deltaMediaOpenHigh

        close_mean = estimations.mediaEstimadorClose

        query = sql.insert(self.table_combo_estimations).values(date=date, candle_min=candle_min, lags=lags, length_frames = length_frames,
                           low_mean=low_mean, low_mean2 = low_mean2, low_mean3 = low_mean3, low_delta = low_delta,
                           high_mean = high_mean, high_mean2=high_mean2, high_mean3=high_mean3, high_delta= high_delta,
                           close_mean=close_mean) 
        result_proxy = self.connection.execute(query)
