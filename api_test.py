from binance.client import Client
from config import BINANCE
from binance.enums import *

client = Client(BINANCE.get("key"), BINANCE.get("secret"))

account = client.get_account()
balances = account["balances"]

# get balance
for balance in balances:
    if balance["asset"] == "BTC":
        print("El balance de Bitcoin es:")
        print(balance["free"])
        break

order = client.create_order(
    symbol="",
    side=SIDE_BUY,
    type=ORDER_TYPE_LIMIT,
    timeInForce=TIME_IN_FORCE_GTC,
    quantity=100,
    price='0.0001'
)
 

