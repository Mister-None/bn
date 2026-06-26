from binance import Client
from time import sleep, localtime, strftime
from dotenv import load_dotenv
from colorama import Fore, init
import sys, requests, os, math
from datetime import datetime, timedelta
import numpy as np
import statistics

init(autoreset=True)

load_dotenv()

BINANCE_API_KEY = os.getenv('binance_api_key')
BINANCE_API_SECRET = os.getenv('binance_api_secret')

class Analyzer:
    def __init__(self, coin):
        self.client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)
        self.symbol = coin.upper() + "USDT" 
        self.selected_coins = []
        self.deal_qty = 0

    def filter1(self):
        tickers = self.client.get_ticker()
        for i in tickers:
            if i['symbol'].endswith('USDT') and 100 <= float(i['quoteVolume']) * 0.000001 and 10 >= float(i['priceChangePercent']) >= -10:
                self.selected_coins.append(i['symbol'])

    def filter2(self):
        ticker = self.client.get_ticker(symbol=self.symbol)
        print('Quote_volume ', 100 <= float(ticker['quoteVolume']) * 0.00001) 
        print('Price_change ' + ticker['priceChangePercent'])

    def filter3(self):
        klines = self.client.get_historical_klines(self.symbol, "1m", "1 day ago UTC")
        original_max_price = [float(i[2]) for i in klines]
        original_min_price = [float(i[3]) for i in klines]
        original_time = [int(int(i[0])/1000) for i in klines]
        max_prices = [float(i[2]) for i in klines]
        min_prices = [float(i[3]) for i in klines]
        time_epochs_max = [int(int(i[0])/1000) for i in klines] 
        time_epochs_min = [int(int(i[0])/1000) for i in klines] 
        buy_times = []
        sell_times = []
        for i in range(len(klines)):
            index_max_price = max_prices.index(max(max_prices))
            index_min_price = min_prices.index(min(min_prices))
            times_max_price = time_epochs_max[index_max_price]
            times_min_price = time_epochs_min[index_min_price]
            time_delta = times_min_price - times_max_price
            fluc = 100 * (max(max_prices) - min(min_prices)) / max(max_prices)
            if time_delta < 0 and min(min_prices) < max(max_prices) and fluc >= 0.5:
                buy_times.append([times_min_price, min(min_prices)])
                sell_times.append([times_max_price, max(max_prices)])
            time_epochs_max.pop(index_max_price)
            time_epochs_min.pop(index_min_price)
            max_prices.pop(index_max_price)
            min_prices.pop(index_min_price)
    
        buy_times.sort(key=lambda x: x[0])
        sell_times.sort(key=lambda x: x[0])
        final_sell_times = [0]
        for i in buy_times:
            for j in sell_times:
                if i[0] < j[0] and i[1] < j[1] and j[0] not in final_sell_times and i[0] > final_sell_times[-1]:
                    final_buy_time_index = int(original_time.index(i[0]))
                    final_sell_time_index = int(original_time.index(j[0]))
                    
                    if j[1] == original_max_price[final_sell_time_index] and i[1] == original_min_price[final_buy_time_index]:
                        self.deal_qty += 1
                        final_sell_times.append(j[0])
                        break
            
    
    def run(self):
        klines = self.client.get_historical_klines(self.symbol, "8h", "1 month ago GMT")
        fair_prices = []
        max_fluctuations = []
        min_fluctuations = []
        volumes = []
        for i in klines:
            open_price = float(i[1])
            max_price = float(i[2])
            min_price = float(i[3])
            close_price = float(i[4])
            volume = float(i[5])

            fair_price = (open_price + max_price + min_price + close_price) / 4
            max_fluctuation = ((max_price - fair_price) / fair_price) * 100
            min_fluctuation = ((fair_price - min_price) / fair_price) * 100              

            fair_prices.append(fair_price)
            max_fluctuations.append(max_fluctuation)
            min_fluctuations.append(min_fluctuation)
            volumes.append(volume)

        total_volume = sum(volumes)
        try:

            VWA_max =  sum(f * v for f, v in zip(max_fluctuations, volumes)) / total_volume
            VWA_min =  sum(f * v for f, v in zip(min_fluctuations, volumes)) / total_volume
            med_max = np.median(max_fluctuations)
            med_min = np.median(min_fluctuations)
            self.filter3()

            if len(sys.argv) > 1:
                print(self.symbol.replace('USDT', ''), round(med_min/2, 2), round(med_max/2, 2), round(3 * (VWA_min + VWA_max), 2))
                print('MED_max(full)', round(med_max, 2))
                print('MED_min(full)', round(med_min, 2))
                print('VMA_max', round(VWA_max, 2))
                print('VMA_min', round(VWA_min, 2))
                self.filter2()
                print(f"{self.deal_qty} - possible trades")
                
                if 3 * med_max >= VWA_max >= med_max and 3 * med_min >= VWA_min >=  med_min and self.deal_qty > 2: print("Valid")
                
                else: print('Not valid')


            elif 3 * med_max >= VWA_max >= med_max and 3 * med_min >= VWA_min >=  med_min and self.deal_qty > 1: 
                print(Fore.LIGHTBLUE_EX + self.symbol.replace('USDT', ''), round(med_min, 2), round(med_max, 2), round(3 * (VWA_min + VWA_max), 2))
        except (ZeroDivisionError, NameError) as e: pass #print(self.symbol.replace('USDT', ''), e)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        bot = Analyzer('')
        bot.filter1()
        for i in bot.selected_coins:
            bot_coin = Analyzer(i.lower().replace('usdt', ''))
            bot_coin.run()
         #   sleep(3)


    else:
        coin_input = sys.argv[1]
        bot = Analyzer(coin_input)
        bot.run()

