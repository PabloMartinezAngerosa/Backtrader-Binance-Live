import os
from config_binance import BINANCE_CREDENTIALS

PRODUCTION = "production"
DEVELOPMENT = "development"

COIN_TARGET = "BTC"
COIN_REFER = "USDT"

ENV = os.getenv("ENVIRONMENT", PRODUCTION)
DEBUG = True
PERSISTENCE_CONNECTION = True
TESTING_PRODUCTION = False
LIVE = False # doble certificacion para operar en Binance. Production y LIVE. Puede estar Production pero en modo testing. 
WINDOWS = False

# TEST KEY
# API Key: rrkkiKYpKfkk6iM88GEG7k6LlK0VX5a4JjfSKaQQQjCVTtRiB9GNUwWVbHiv0MBf
# Secret Key: YvKlog7B5wlbUIPKLpPT9Aos12S92X0OJfsyCDGythVuN1fbmmNxiQmSNYH3nlgi


# PRODUCTION
 # ExcI0XeCRrWCUfklhGggIFCCNjn9gwB0bsU79qbE0kuASPzrqfOR1BZDhBuJ8lSj 
 # gAPN5Wgv7yeNfxt8eyO8IxmMtyvc235FZsuRngYHek3E5263JqlBs1FtB5xxNQn5

TESTING_PRODUCTION_DATE = {
  "from":1615145399999,
  "to":1615150800172
}

BINANCE = BINANCE_CREDENTIALS

TELEGRAM = {
  "channel": "t.me/libertad_kamikaze_bot",
  "bot": "1626640400:AAEJeXYbxMIsNiDu7okdHHHU7JuHsmn0swo"
}

SQL = {
  "user" : "root",
  "pass" :  "libertad" 
}

STRATEGY = {
  "length_frames": 20,
  "lags": 5,
  "candle_min":1,
  "kline_interval": "KLINE_INTERVAL_1MINUTE",
  "mean_tick_prod":26,
  "mean_tick_dev":26
}

# for standalone and test
SANDBOX_INITAL_CAPITAL = 1000

print("ENV = ", ENV)