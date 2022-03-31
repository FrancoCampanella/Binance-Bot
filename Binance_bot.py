from binance.client import Client
import time
from binance import ThreadedWebsocketManager
from binance.enums import *

api_key = 'N6zhaClblFVq839Fe91NwtNPFcvY3g6cWoBEVtwI126o6exHAPGjNbjR3pEpvtVq'
api_secret = 'fFkL2gnAvZ1NGJfXYnaTEdhOnBly1Wa0y6OodLLolPBdrwHb9EmenVEIJ1Z4fNgx'

client = Client(api_key, api_secret, tld='com')

futureBalance = client.futures_account_balance()
#print(futureBalance)

print("BNB ", futureBalance[0].get('balance') )
print("USDT ", futureBalance[1].get('balance') )
print("BUSD ", futureBalance[2].get('balance') )