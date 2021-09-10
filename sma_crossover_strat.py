import oandapyV20
#import oandapyV20.endpoints.instruments as instruments
#import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.trades as trades
#import pandas as pd
import matplotlib.pyplot as plt
import time
import Indicators as ind
#initiating API connection and defining trade parameters
token = r"C:\Users\Nishant\Desktop\algorithmic trading udemy\token_oanda.txt"
client = oandapyV20.API(access_token=open(token,'r').read(),environment="practice")
account_id = "101-002-20536476-001"

#defining strategy parameters
tickers = ['EUR_USD','GBP_USD','USD_CHF','AUD_USD'] #currency pairs to be included in the strategy

pos_size = 1000 #max capital allocated/position size for any currency pair
upward_sma_dir = {}
dnward_sma_dir = {}
for i in tickers:
    upward_sma_dir[i] = False
    dnward_sma_dir[i] = False


def trade_signal(df,curr):
    "function to generate signal"
    global upward_sma_dir, dnward_sma_dir
    signal = ""
    if df['sma_fast'][-1] > df['sma_slow'][-1] and df['sma_fast'][-2] < df['sma_slow'][-2]:
        upward_sma_dir[curr] = True
        dnward_sma_dir[curr] = False
    if df['sma_fast'][-1] < df['sma_slow'][-1] and df['sma_fast'][-2] > df['sma_slow'][-2]:
        upward_sma_dir[curr] = False
        dnward_sma_dir[curr] = True  
    if upward_sma_dir[curr] == True and min(df['K'][-1],df['D'][-1]) > 25 and max(df['K'][-2],df['D'][-2]) < 25:
        signal = "Buy"
    if dnward_sma_dir[curr] == True and min(df['K'][-1],df['D'][-1]) < 75 and max(df['K'][-2],df['D'][-2]) > 75:
        signal = "Sell"

    plt.subplot(211)
    plt.plot(df.iloc[-50:,[3,-2,-1]])
    plt.title('SMA Crossover & Stochastic')
    plt.legend(('close','sma_fast','sma_slow'),loc='upper left')
    
    plt.subplot(212)
    plt.plot(df.iloc[-50:,[-4,-3]])
    plt.hlines(y=25,xmin=0,xmax=50,linestyles='dashed')
    plt.hlines(y=75,xmin=0,xmax=50,linestyles='dashed')
    plt.show()
    
    return signal

def main():
    global tickers
    try:
        r = trades.OpenTrades(accountID=account_id)
        open_trades = client.request(r)['trades']
        curr_ls = []
        for i in range(len(open_trades)):
            curr_ls.append(open_trades[i]['instrument'])
        tickers = [i for i in tickers if i not in curr_ls]
        for currency in tickers:
            print("Currency ",currency)
            data = ind.candles(currency,client)
            ohlc_df = ind.stochastic(data,14,3,3)
            ohlc_df = ind.SMA(ohlc_df,100,200)
            signal = trade_signal(ohlc_df,currency)
            if signal == "Buy":
                ind.market_order(currency,pos_size,3*ind.ATR(data,120),client,account_id)
                print("New long position initiated for ", currency)
            elif signal == "Sell":
                ind.market_order(currency,-1*pos_size,3*ind.ATR(data,120))
                print("New short position initiated for ", currency)
    except:
        print("error occurred....")


# Continuous execution        
start=time.time()
timeout = time.time() + 60*15*1  
while time.time() <= timeout:
    try:
        print("passthrough at ",time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        main()
        time.sleep(300 - ((time.time() - start) % 300.0)) #5 minute interval
    except KeyboardInterrupt:
        print('\n\nKeyboard Interruption. Exiting.')
        exit()