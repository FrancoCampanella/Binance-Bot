from numpy import double, int32
from scipy.fftpack import diff
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
from sympy import *

#FALTA:
    #Ejecutar adecuadamente el loop asincronico (archivo async para luego incorporar en create_grid)
    #Estrategias segun tendencia (alcista, bajista, neutral)
    #Creado de la grilla de compra/venta segun valores extremos generados por la estrategia
    #Revisar tendencia

class trading_bot:
    def __init__(self) -> None:
        self.exchange = ccxt.binance({'countries': 'US'})
        self.candles = 150
        self.timeframe = '5m'
        self.symbol = 'BTC/BUSD'
        self.bars = self.exchange.fetch_ohlcv(self.symbol, timeframe=self.timeframe, limit=self.candles)
        self.df = pd.DataFrame(self.bars, columns=['time','open','high','low','close', 'volume'])
        self.client = Client(config.api_key, config.api_secret, tld='com')  
        self.loop = asyncio.get_event_loop()

    def append_candle(self):
        bar = self.exchange.fetch_ohlcv(self.symbol, timeframe=self.timeframe, limit=1)
        dfNew = pd.DataFrame(bar, columns=['time','open','high','low','close', 'volume'])
        self.df = pd.concat([self.df, dfNew] ,ignore_index=True)
        self.df = self.df.drop([0], axis=0)
        print("Vela agregada")

    def buy_order(self, qty, tendence):
        print(f"compra {qty} BTC")

    def sell_order(self, qty, tendence):
        print(f"vende {qty} BTC")

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
    
    def moving_avarage(self, dataFrame, length):
        sma = self.df.ta.sma(close=dataFrame['close'] , length=length, append=True)
        fig, ax = plt.subplots()
        ax.plot(dataFrame["time"][:], sma[:], color='b')
        ax.plot(dataFrame["time"][:], dataFrame['close'], color='r')
        ax.grid()
        plt.show()
        print(sma)

    async def create_grid(self, flag, tendence, change, upper, lower):
        client = await AsyncClient.create(tld='com')
        bm = BinanceSocketManager(client)
        #Abro socket
        ts = bm.trade_socket('BTCBUSD')
        #Comienza la transmision de datos de forma asincronica
        async with ts as tscm:
            min_aux = time.localtime().tm_min
            while True:
                res = await tscm.recv()
                h = res['T']/1000/60/60
                min = int32((h - int32(res['T']/1000/60/60))*60)
                if min == (min_aux+1):
                    print("Nueva vela de 1m: ", min)
                    min_aux = min_aux + 1
                    self.append_candle()
                    self.loop.stop()
                    print("Termino el loop")
        await client.close_connection()
        #qty_BUSD = self.client.futures_account_balance()[-1]['balance']/10
        #precio_ini = precio
        #Grilla fina
        #if (tendence == "alcista") and (flag == "short"):
        #    max = upper + 500
        #    min = lower - 200
        #    cuadro_up = (max - precio_ini)/6
        #    cuadro_dn = (precio_ini - min)/4
            #meter compra qty_BUSD
            #if precio == (precio_ini + cuadro_up) --> invierto qty_BUSD*2, precio_ini = precio_ini + cuadro
            #if precio == (precio_ini - cuadro_dn) --> cierro ordenes
            #if profit > 1,5 --> cierro ordenes


        #A la cantidad que tengo en mi billetera la divido en 10:
        #1. Coloco 5 ordenes de venta/short por encima del precio actual (habilitar flag en strategy)
            #C/U de las ordenes superiores duplican el monto invertido en las ordenes precedentes
        #2. Coloco 5 ordenes de compra/long por debajo del precio actual (habilitar flag en strategy)
            #C/U de las ordenes inferiores duplican el monto invertido en las ordenes precedentes

    

    #Funcionamiento: si las velas de 5m atraviezan la curva de media movil 50 se observa un cambio de tendencia
                    # se verifica la tendencia mediante dos mecanismos: 
                    # 1. Pendiente de la curva de medias moviles 25 (con velas de 5m) mayor/menor a 10
                    # 2. bandas de bollinger y stochrsi para elas de 1h confirman la tendencia por venir
    def check_tendence(self):
        #Utilizo un cronograma temporal superior para verificar la tendencia en 5m
        bars_15m = self.exchange.fetch_ohlcv('BTC/BUSD', timeframe='15m', limit=150)
        df_new = pd.DataFrame(bars_15m, columns=['time','open','high','low','close', 'volume'])
        
        #Media movil de 25 con velas de 15m
        sma_25 = df_new.ta.sma(close=df_new['close'] , length=25, append=True)

        #Media movil de 50 con velas de 15m
        sma_50 = df_new.ta.sma(close=df_new['close'] , length=50, append=True)

        #Se cuenta la cantidad de velas que atraviezan la media movil de 50 (con velas de 15m)
        cont_up=0   
        cont_dn=0
        for i in range(0, len(sma_50)):
            if sma_50[i] <= self.df['close'][i]:
                cont_up=cont_up+1
                cont_dn=0
            else:
                cont_dn=cont_dn+1
                cont_up=0

        #Calculo de la derivada para conocer la pendiente de la curva media movil 25 (con velas de 15m)
        sma_25_sin_nan = sma_25.fillna(0)
        n = diff(sma_25_sin_nan)

        if (n[len(n)-1]>=10) and (cont_up>=10):
            tendence = "alcista"     
            #print("Tendencia alcisata")
        elif (n[len(n)-1]<=-10) and (cont_dn>=10):
            tendence = "bajista"
            #print("Tendencia bajista")
        else:
            tendence = "neutra"
            #print("Tendencia neutra")
        
        return tendence

    def tendence_change(self):
        #Utilizo un marco temporal superior (1h) para verificar la tendencia general
        candles = 50
        bars_1h = self.exchange.fetch_ohlcv('BTC/BUSD', timeframe='1h', limit=candles)
        df = pd.DataFrame(bars_1h, columns=['time','open','high','low','close', 'volume'])

        #Calculo indicadores
        bollinger = df.ta.bbands()
        rsi = df.ta.stochrsi(close=df['close'])

        #Si se cumple la estrategia en 1h, entonces efectivamente podria producirse un cambio de tendencia
        if (rsi["STOCHRSIk_14_14_3_3"][candles-1] >= 90) and (df['close'][candles-1] >= bollinger["BBU_5_2.0"][candles-2]):
            change = "change_dn"
        elif (rsi["STOCHRSIk_14_14_3_3"][candles-1] <= 10) and (df['close'][candles-1] <= bollinger["BBU_5_2.0"][candles-2]):
            change = "change_up"
        else: 
            change = "none"
        return change


    def strategy(self):
        #Calculo de indicadores
        bollinger = self.df.ta.bbands()
        rsi = self.df.ta.stochrsi(close=self.df['close'])

        upBBand = double(bollinger["BBU_5_2.0"][self.candles-2])
        dnBBand = double(bollinger["BBL_5_2.0"][self.candles-2])

        #Comprobación de tendencia:
        #                  Al alza: RSI al 90% y banda de bollinger superior al 90%
        #                  A la baja: RSI al 10% y banda de bolllinger inferior al 10%
        if (rsi["STOCHRSIk_14_14_3_3"][self.candles-1] >= 85) and (self.df['close'][self.candles-1] >= upBBand*0.9982):
            try:
                self.loop.run_until_complete(self.create_grid(flag = 'short', 
                                                            tendence = self.check_tendence(), 
                                                            change = self.tendence_change(), 
                                                            upper = upBBand, 
                                                            lower = dnBBand))
            except RuntimeError:
                print("Termino el loop")
        elif (rsi["STOCHRSIk_14_14_3_3"][self.candles-1] <= 15) and (self.df['close'][self.candles-1] <= dnBBand*1.0015):
            try:
                self.loop.run_until_complete(self.create_grid(flag = 'long',
                                            tendence = self.check_tendence(), 
                                            change = self.tendence_change(), 
                                            upper = upBBand, 
                                            lower = dnBBand))
            except RuntimeError:
                print("Termino el loop")
        else: print("No operar")
        print("Bollinger superior: ", upBBand)
        print("Limite superior: ",upBBand*0.9982)
        print("Bollinger inferior: ",dnBBand)
        print("Limite inferior: ",dnBBand*1.0015)
        print("RSI: ", rsi["STOCHRSIk_14_14_3_3"][self.candles-1])
        print("Vela actual: ", self.df['close'][self.candles-1])
        print(self.check_tendence())
        print(self.tendence_change())




if __name__ == "__main__":
    bot = trading_bot()
    while True:
        bot.strategy()
    #bot.create_grid()
    #bot.bollinger_band()
    #bot.stochRSI()