from cv2 import sqrt
from flask import flash
from numpy import double, float64, int32, short
from scipy.fftpack import diff
from sympy import false, true
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

import math
import matplotlib.pyplot as plt
import requests

exchange = ccxt.binance({'countries': 'US'})
candles = 60
k = 0
time_frame = 15
timeframe = str(time_frame)+'m'

def telegram_bot_sendtext(bot_message):

    bot_token = '5330958791:AAGBvA118jpFYXafPqbz7mtH8m51lLlGVs8'
    bot_chatID = '1786071046'
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message

    response = requests.get(send_text)

    return true

def BollingerBands(df, sma_period=20, nro_StDev=2):
    #Media movil simple
    sma = float64(df.ta.sma(sma_period))
    close = float64(df['close'])

    #Calculo de desviacion estandar
    sum = 0
    for i in range(20,candles):
        sum = sum + math.pow((close[i] - sma[i]),2)
    StDev =  math.sqrt(sum/candles)

    #Calculo de banda media
    MBB = math.fsum(close)/candles
    
    #Calculo banda superior
    UPBB = MBB + (nro_StDev*StDev)

    #Calculo banda inferior
    DNBB = MBB - (nro_StDev*StDev)

    bollinger = {"upBollinger": UPBB, "midBollinger": MBB, "dnBollinger": DNBB}

    return bollinger


def indicators():
    bars = exchange.fetch_ohlcv('BTC/BUSD', timeframe=timeframe, limit=candles)
    df = pd.DataFrame(bars, columns=['time','open','high','low','close', 'volume'])

    #Calculo indicadores
    bollinger = BollingerBands(df)
    upBBand = bollinger["upBollinger"]  #*0.9980
    dnBBand = bollinger["dnBollinger"]  #*1.0015

    rsi = df.ta.stochrsi(close=df['close'])
    stoch_rsi = rsi["STOCHRSIk_14_14_3_3"][candles-1]
    print(f"Price: {df['close'][candles-1]} /BBUP: {upBBand} /BBDN: {dnBBand} /RSI: {stoch_rsi}")

    return stoch_rsi, upBBand, dnBBand

def min_15(min):
    if (min>0) and (min<15):
        min_aux = 15
    elif (min>15) and (min<30):
        min_aux = 30
    elif (min>30) and (min<45):
        min_aux = 45
    else:
        min_aux = 0
    return min_aux


async def main():
    client = await AsyncClient.create(tld='com')
    bm = BinanceSocketManager(client)

    #Abro socket
    ts = bm.trade_socket('BTCBUSD')

    #Calculo de indicadores
    stoch_rsi, upBBand, dnBBand = indicators()
    between = (upBBand - dnBBand)*0.15
    short_flag = false
    long_flag = false
    flag_report = false
    positive_op = 0
    negative_op = 0
    time_ev = -1
    aux_price_short = None
    aux_price_long = None

    #Comienza la transmision de datos de forma asincronica
    async with ts as tscm:
        t = time.localtime().tm_min
        min_aux = min_15(t)
        while True:
            res = await tscm.recv()
            h = res['T']/1000/60/60
            min = int((h - int(res['T']/1000/60/60))*60)

            #Actualizo indicadores y velas cada un minuto
            if min == min_aux:
                print("Nueva vela: ", min)
                stoch_rsi, upBBand, dnBBand = indicators()
                flag_report = false
            
            #Reinicio los flags cuendo se encuentran dentro de la banda central
            if (stoch_rsi<=70) and (stoch_rsi>=30):
                short_flag = false
                long_flag = false
 
            #Descomentar para velas de 1 min
            if (stoch_rsi >= 90) and (double(res['p']) >= (upBBand - between)) and (short_flag == false):
                short_flag = telegram_bot_sendtext("Short")
                aux_price_short = double(res['p']) 
                if min_aux == 45:
                    time_ev = 15
                else:  
                    time_ev = min_aux + 2*time_frame
                #time_ev = min_aux + 5*time_frame
            elif (stoch_rsi <= 10) and (double(res['p']) <= (dnBBand + between)) and (long_flag == false):
                long_flag = telegram_bot_sendtext("Long")
                aux_price_long = double(res['p'])
                if min_aux == 45:
                    time_ev = 15
                else:  
                    time_ev = min_aux + 2*time_frame
                #time_ev = min_aux + 5*time_frame

            
            #Transcurrido 2 veces el marco temporal, se evalua si la operacion fue exitosa
            if min == time_ev:
                if aux_price_short == None:
                    pass
                else:
                    if aux_price_short > double(res['p']):
                        positive_op = positive_op + 1
                    elif aux_price_short < double(res['p']):
                        negative_op = negative_op + 1

                if aux_price_long == None:
                    pass
                else:
                    if aux_price_long < double(res['p']):
                        positive_op = positive_op + 1
                    elif aux_price_long > double(res['p']):
                        negative_op = negative_op + 1
                time_ev = -1
                aux_price_short = None
                aux_price_long = None
                print("Operaciones positivas: " + str(positive_op) + " /Operaciones negativas: " + str(negative_op))

            #Envio reporte de operaciones positivas y negativas
            if (min == 0) and (flag_report == false):
                operations = "Positivas: " + str(positive_op) + "/ "+ "Negativas: " + str(negative_op)
                flag_report = telegram_bot_sendtext(operations)

    await client.close_connection()

if __name__ == "__main__":
    #indicators()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
#strategy()
#if min == (min_aux+1):
#    print("Nueva vela: ", min)
#    stoch_rsi, upBBand, dnBBand = indicators()
#    min_aux = min_aux + time_frame
#    flag_report = false
#    if min_aux == 59:
#        min_aux=-1