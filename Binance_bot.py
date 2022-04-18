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

import matplotlib.pyplot as plt

class trading_bot:
    def __init__(self) -> None:
        self.exchange = ccxt.binance({'countries': 'US'})
        self.candles = 100
        self.bars = self.exchange.fetch_ohlcv('BTC/BUSD', timeframe='15m', limit=self.candles)
        self.df = pd.DataFrame(self.bars, columns=['time','open','high','low','close', 'volume'])
        #print(self.df)

    def append_candle(self):
        bar = self.exchange.fetch_ohlcv('BTC/BUSD', timeframe='15m', limit=1)
        dfNew = pd.DataFrame(bar, columns=['time','open','high','low','close', 'volume'])
        self.df = pd.concat([self.df, dfNew] ,ignore_index=True)
        self.df = self.df.drop([0], axis=0)

    def buy_order(self):
        #self.client = Client(config.api_key, config.api_secret, tld='com')
        bollinger = self.bollinger_band(self.df)

    def bollinger_band(self):
        bollinger = self.df.ta.bbands()
        fig, ax = plt.subplots()
        ax.plot(self.df["time"][:], bollinger["BBL_5_2.0"][:], color='b')
        ax.plot(self.df["time"][:], bollinger["BBM_5_2.0"][:], color='r')
        ax.plot(self.df["time"][:], bollinger["BBU_5_2.0"][:], color='b')
        ax.plot(self.df["time"][:], self.df["close"][:], color='g')
        ax.grid()
        plt.show()
        print(bollinger)

    def stochRSI(self):
        #FALTA COLOCAR DOS GRAFICAS POR SEPARADO 
        #1. GRAFICA DE PRECIOS
        #2. GRAFICA DEL ESTOCASTICO
        #fig, ax = plt.subplots(2, 1, 2)
        #ax.plot(self.df["time"][:], self.df["close"][:], color='g')

        rsi = self.df.ta.stochrsi(close=self.df['close'])
        fig, ax = plt.subplots()
        ax.plot(self.df["time"][:], rsi["STOCHRSIk_14_14_3_3"][:], color='b')
        ax.plot(self.df["time"][:], rsi["STOCHRSId_14_14_3_3"][:], color='r')
        ax.grid()
        plt.show()

    def strategy(self):
        bollinger = self.df.ta.bbands()
        rsi = self.df.ta.stochrsi(close=self.df['close'])
        if (rsi["STOCHRSIk_14_14_3_3"][self.candles-1] >= 90) and (self.df['close'] >= bollinger["BBU_5_2.0"][self.candles-1]):
            #PRECIO SOBRE VENDIDO - orden de venta
        if (rsi["STOCHRSIk_14_14_3_3"][self.candles-1] <= 10) and (self.df['close'] <= bollinger["BBU_5_2.0"][self.candles-1]):
            #PRECIO SOBRECOMPRADO - orden de compra




if __name__ == "__main__":
    bot = trading_bot()
    #bot.buy_order()
    #help(ta.stochrsi)
    bot.bollinger_band()
    #bot.stochRSI()