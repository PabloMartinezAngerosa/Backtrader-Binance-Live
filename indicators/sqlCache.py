import sqlalchemy as sql

engine = sql.create_engine("mysql+mysqlconnector://root:root@localhost/binance")

initial_q = """INSERT INTO combo_estimations
(date,candle_min,lags,low_mean,low_mean2,low_mean3,high_mean,high_mean2,high_mean3,high_delta, low_delta,close_mean)
VALUES"""

values_q = ",".join(["""('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')""".format(
    "12:23:23",
    23,
    5,
    234,
    234,
    234,
    234,
    234,
    234,
    234,
    234,
    234
    )])

q = initial_q + values_q
print(q)
engine.execute(q)