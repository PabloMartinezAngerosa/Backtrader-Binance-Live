import os
from config_binance import BINANCE_CREDENTIALS

PRODUCTION = "production"
DEVELOPMENT = "development"

COIN_TARGET = "BTC"
COIN_REFER = "USDT"

ENV = os.getenv("ENVIRONMENT", DEVELOPMENT)
MULTIPLE_INSTANCE = False
DEBUG = True
PERSISTENCE_CONNECTION = False
TESTING_PRODUCTION = False
UPDATE_PARAMS_FUERZA_BRUTA = False
LIVE = False # doble certificacion para operar en Binance. Production y LIVE. Puede estar Production pero en modo testing. 
WINDOWS = False
PHEMEX_PRICE = False # si va a buscar precio en phemex desde automatizacion
# TEST KEY
# API Key: rrkkiKYpKfkk6iM88GEG7k6LlK0VX5a4JjfSKaQQQjCVTtRiB9GNUwWVbHiv0MBf
# Secret Key: YvKlog7B5wlbUIPKLpPT9Aos12S92X0OJfsyCDGythVuN1fbmmNxiQmSNYH3nlgi


# PRODUCTION
 # ExcI0XeCRrWCUfklhGggIFCCNjn9gwB0bsU79qbE0kuASPzrqfOR1BZDhBuJ8lSj 
 # gAPN5Wgv7yeNfxt8eyO8IxmMtyvc235FZsuRngYHek3E5263JqlBs1FtB5xxNQn5

TESTING_PRODUCTION_DATE = {
  "from":1627942499999,
  "to":1627967700096
}

BINANCE = BINANCE_CREDENTIALS

TELEGRAM = {
  "channel": "-471648486",
  "bot": "1626640400:AAEJeXYbxMIsNiDu7okdHHHU7JuHsmn0swo"
}
#https://api.telegram.org/bot1626640400:AAEJeXYbxMIsNiDu7okdHHHU7JuHsmn0swo/getUpdates
# group id 1626640400
'''
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
'''

SQL = {
  "user" : "root",
  "pass" :  "libertad" 
}

STRATEGY = {
  "max_profit": (130/100)**(1/60),
  "min_profit": (80/100)**(1/60),
  "length_frames": 25,
  "lags": 5,
  "candle_min":720,
  "kline_interval": "KLINE_INTERVAL_12HOUR",
  "mean_tick_prod":418,
  "mean_tick_dev":418
}

PHEMEX = {
  "testnet_url" : "https://testnet.phemex.com/spot/trade/BTCUSDT",
  "production_url" : "https://phemex.com/spot/trade/BTCUSDT"
}

PHEMEX_URL = PHEMEX.get("production_url")

# for standalone and test
SANDBOX_INITAL_CAPITAL = 100

print("ENV = ", ENV)

ACUM_CAPITAL_ALL =  {
  "acum_capital" : 100,
  "acum_capital_binance" : 100,
  "acum_capital_lx2" : 100,
  "acum_capital_lx5" : 100,
  "acum_capital_lx10" : 100,
  "acum_capital_lx20" : 100,
  "acum_capital_lx50" : 100,
  "acum_capital_lx100" : 100,
  "acum_capital_lx125" : 100
}

BUY_OPERATION_INFO = {
  "is_order": False,
  "buy_price_binance": 0,
  "buy_price": 0,
  "buy_price_actual": 0
}
# multiple instance testing
MULTIPLE_INSTANCE_DATE = [
  [1624515299999, 1624548600268],
  [1624687199999,1624727700149],
  [1624851899999, 1624902300138],
  [1624946399999, 1624991400037],
  [1625027399999, 1625058000179],
  [1625114699999, 1625157900162],
  [1625200199999,1625244300266],
  [1625286599999,1625329800034],
  [1625377499999,1625419800048],
  [1625633099999,1625684400040],
  [1625719499999,1625761800158],
  [1625807699999,1625855400145],
  [1625896799999,1625951700255]
]

