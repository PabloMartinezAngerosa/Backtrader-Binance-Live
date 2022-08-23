from binance.client import Client
#from binance import exceptions.BinanceAPIException
from binance.exceptions import BinanceAPIException
from config import BINANCE
from binance.enums import *

from binance_f import RequestClient
from binance_f.constant.test import *
from binance_f.base.printobject import *
from binance_f.model.constant import *


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


interval = KLINE_INTERVAL_15MINUTE 

client = Client(BINANCE.get("key"), BINANCE.get("secret"))
futureBalance = client.futures_account_balance()

print(futureBalance)
# print(futureBalance)
# print("USDT ", futureBalance[1].get('balance'))


# es la otra libreria... puede ser una opcion, hay buennos ejemplos, se ve la libreria, y se puede usar con apalancamiento bitcoin
# client = RequestClient(api_key=BINANCE.get("key"), secret_key=BINANCE.get("secret"))
# Done
# client.change_initial_leverage(symbol = "BTCUSDT", leverage=1)


client.futures_change_leverage(symbol='BTCUSDT', leverage=1)

#TODO probar el try/catch

try:
    order_future = client.futures_create_order(
        symbol='ADAUSDT',
        type='MARKET',
        side='BUY',
        positionSide='SHORT',
        quantity=20
    )
except BinanceAPIException as e:
    print(e.status_code)
    print(e.message)


#print("Future active orders")
#print(client.futures_get_all_orders(symbol='BTCUSDT'))

# print(order_future)
#print("Try cancel order")
#cancel = client.cancel_order(symbol='BTCUSDT', orderId=56229191695)



