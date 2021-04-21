from binance.client import Client
from config import BINANCE
from binance.enums import *

TRADE_SYMBOL = 'BTCUSDT'
TRADE_QUANTITY = 0.004536

client = Client(BINANCE.get("key"), BINANCE.get("secret"))


account = client.get_account()
balances = account["balances"]

print(balances)
# get balance
for balance in balances:
    if balance["asset"] == "BTCUSDT":
        print("El balance de BTCUSDT es:")
        print(balance["free"])
        break

# print(client.get_exchange_info())

def order(side, quantity, symbol,  order_type = ORDER_TYPE_MARKET):
    try:
        order = client.create_order(
            symbol=symbol,
            side=side,
            type=order_type,
            quantity=quantity
        )
        print(order)
    except Exception as e:
        print(e)
        return False
    return True

order_status = order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)

print("Se realizo la compra  con estatus" + str(order_status))