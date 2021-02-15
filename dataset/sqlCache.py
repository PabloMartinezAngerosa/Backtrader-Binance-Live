import sqlalchemy as sql
from config import SQL

class SqlCache():
    __init__(self):
        self.engine = sql.create_engine("mysql+mysqlconnector://" +   SQL.get("user") + ":" + SQL.get("pass")  + "@localhost/binance")
        self.metadata = sql.MetaData()
        self.connection = self.engine.connect()
        self.table_combo_estimations = sql.Table('combo_estimations', self.metadata, autoload=True, autoload_with=self.engine)

    def insert_estimators(self, date, candle_min, lags, estimations):


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

        query = sql.insert(self.table_combo_estimations).values(date=date, candle_min=candle_min, lags=lags, 
                           low_mean=low_mean, low_mean2 = low_mean2, low_mean3 = low_mean3, low_delta = low_delta,
                           high_mean = high_mean, high_mean2=high_mean2, high_mean3=high_mean3, high_delta= high_delta,
                           close_mean=close_mean) 
        ResultProxy = self.connection.execute(query)
        print(ResultProxy)
