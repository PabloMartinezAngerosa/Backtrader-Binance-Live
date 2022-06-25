import pandas as pd
import math
import os.path
import time
from binance.client import Client
from datetime import timedelta, datetime
from dateutil import parser
from tqdm import tqdm_notebook #(Optional, used for progress-bars)
from config import BINANCE

client = Client(BINANCE.get("key"), BINANCE.get("secret"))

# https://stackoverflow.com/questions/70306172/time-difference-with-binance-server
# diferencias chicas... 646 es milisegundos osea 0.646 segundo es q esta sync.
# importante para tareas de kron, cada 1 minuto ir a buscar... price si bla bla, para production


# Get Server Time
def get_server_time():
    ts = client.get_server_time()['serverTime']
    server_time = datetime.utcfromtimestamp(ts / 1000).strftime('%Y-%m-%d %H:%M:%S')
    return server_time

print(round(time.time()*1000))
print(client.get_server_time()['serverTime'])

# Check if computer time is the same as server time
if time.time()*1000 != client.get_server_time()['serverTime']:
    print("There is a problem in time sync.")
else:
    print("Your computer time matches server time.")