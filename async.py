import asyncio
from binance import AsyncClient, BinanceSocketManager
import pandas as pd 
import pandas_ta as ta

async def main():
    client = await AsyncClient.create(tld='com')
    bm = BinanceSocketManager(client)
    # start any sockets here, i.e a trade socket
    ts = bm.trade_socket('BTCBUSD')
    # then start receiving messages
    cont = 0
    open_price=0
    
    async with ts as tscm:
        while True:
            res = await tscm.recv()
            state = res['m']
            print(res)
            if state == True:
                loop.stop()
    await client.close_connection()

    

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except RuntimeError:
        print("Termino el loop")




exchange = ccxt.binance({'countries': 'US'})
bars = exchange.fetch_ohlcv('BTC/BUSD', timeframe='15m', limit=100)
df = pd.DataFrame(bars, columns=['time','open','high','low','close', 'volume'])
bar = exchange.fetch_ohlcv('BTC/BUSD', timeframe='15m', limit=1)
dfNew = pd.DataFrame(bar, columns=['time','open','high','low','close', 'volume'])
df = pd.concat([df, dfNew] ,ignore_index=True)
df = df.drop([0], axis=0)
#longitud del df = df.shape[0]
print(df.shape[0])


import asyncio
from binance import AsyncClient, BinanceSocketManager
import pandas as pd 
import pandas_ta as ta

async def main():
    client = await AsyncClient.create(tld='com')
    bm = BinanceSocketManager(client)
    # start any sockets here, i.e a trade socket
    ts = bm.trade_socket('BTCBUSD')
    # then start receiving messages
    cont = 0
    open_price=0
    async with ts as tscm:
        while True:
            res = await tscm.recv()
            state = res['m']
            if state == True:
                cont = cont + 1
                try: 
                    data = {'time':res['T'], 'open': open_price, 'high': max_p, 'low': min_p, 'price':res['p'], 'candle':res['m']}
                    #self.dataframe = pd.DataFrame(data, columns=['time','open','high','low','close','candle'])
                    print(data)
                    open_price = res['p']
                    del self.candle[:]
                    max_p = 0
                    min_p = 1e20
                except:
                    open_price = res['p']
                    del self.candle[:]
                    max_p = 0
                    min_p = 1e20
            else:
                self.candle.append(res['p'])
                p_act = res['p']
                for p_ant in self.candle:
                    if p_act > p_ant:
                        max_p = p_act
                    if p_act < p_ant:
                        min_p = p_act

    await client.close_connection()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
