import config
import asyncio
from binance import AsyncClient, BinanceSocketManager
import pandas as pd 
import pandas_ta as ta
import ccxt 
import datetime as dt

from binance.client import Client
import time
from binance import ThreadedWebsocketManager
from binance.enums import *

exchange = ccxt.binance({'countries': 'US'})
bars = exchange.fetch_ohlcv('BTC/BUSD', timeframe='15m', limit=100)
df = pd.DataFrame(bars, columns=['time','open','high','low','close', 'volume'])
bar = exchange.fetch_ohlcv('BTC/BUSD', timeframe='15m', limit=1)
dfNew = pd.DataFrame(bar, columns=['time','open','high','low','close', 'volume'])
df = pd.concat([df, dfNew] ,ignore_index=True)
df = df.drop([0], axis=0)
#longitud del df = df.shape[0]
print(df.shape[0])
