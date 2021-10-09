import pandas as pd 
import numpy as np 

def macd(stock):
    exp1 = stock['Close'].ewm(span = 12, adjust = False).mean()
    exp2 = stock['Close'].ewm(span = 26, adjust = False).mean()
    macd = pd.DataFrame(exp1 - exp2).rename(columns = {'Close':'macd'})
    signal = pd.DataFrame(macd.ewm(span = 9, adjust = False).mean()).rename(columns = {'macd':'signal'})
    hist = pd.DataFrame(macd['macd'] - signal['signal']).rename(columns = {0:'hist'})

    frames =  [macd, signal, hist]
    stock_macd = pd.concat(frames, join = 'inner', axis = 1)

    def implement_macd_strategy(prices, data): 
        
        # buat empty list, untuk wadah. 
        buy_price = []
        sell_price = []
        macd_signal = []
        signal = 0

        for i in range(len(data)):
            if data['macd'][i] > data['signal'][i]:
                if signal != 1:
                    buy_price.append(prices[i])
                    sell_price.append(np.nan)
                    signal = 1
                    macd_signal.append(signal)
                else:
                    buy_price.append(np.nan)
                    sell_price.append(np.nan)
                    macd_signal.append(0)
            elif data['macd'][i] < data['signal'][i]:
                if signal != -1:
                    buy_price.append(np.nan)
                    sell_price.append(prices[i])
                    signal = -1
                    macd_signal.append(signal)
                else:
                    buy_price.append(np.nan)
                    sell_price.append(np.nan)
                    macd_signal.append(0)
            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                macd_signal.append(0)
                
        return macd_signal

    macd_signal = implement_macd_strategy(stock['Close'], stock_macd)
    macd_signal = pd.DataFrame(macd_signal).rename(columns = {0:'macd_signal'}).set_index(stock.index)

    return macd_signal