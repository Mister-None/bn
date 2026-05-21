from binance import Client
from time import sleep, strftime
from dotenv import load_dotenv
from colorama import Fore, init
import sys, requests, os, math, subprocess

init(autoreset=True)

load_dotenv(dotenv_path=os.getenv('DOTENV_FILE_PATH'))

BINANCE_API_KEY = os.getenv('binance_api_key')
BINANCE_API_SECRET = os.getenv('binance_api_secret')
TG_NOTIFICATOR_PATH = os.getenv('tg_notificator_path')
trading_sum = 100

buy_threshold = 1 - float(sys.argv[2]) / 100
take_profit = 1 + float(sys.argv[3]) / 100
stop_loss = 1 - float(sys.argv[4]) / 100

selected_coin = sys.argv[1] + ' 👉   -' + sys.argv[2] + '  ' + sys.argv[3] + '  -' + sys.argv[4]

upd_120_hours = [i * 7200 for i in range(6)]
upd_8_hours = [i * 480 for i in range(90)]

class StableTrader:
    def __init__(self, coin):
        self.client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)
        self.coin_qty = float(self.client.get_asset_balance(asset=coin_input.upper())['free']) 
        self.symbol = coin.upper() + "USDT" 
        self.hold_crypto =  False
        self.buy_price = 0.0
        self.coin_step = 0
        self.counter_avg = 0
        self.total_profit = 0
        self.buy_zone = 0
        self.message = ''

    def get_avg_price(self):
        try:
            klines = self.client.get_historical_klines(self.symbol, "1m", "8 hours ago GMT")
            prices = [(float(i[1]) + float(i[2]) + float(i[3]) + float(i[4])) / 4 for i in klines] 
            return sum(prices) / len(prices)
        except Exception as e: 
            print(Fore.LIGHTRED_EX + str(e))
            subprocess.run(['python', TG_NOTIFICATOR_PATH, str(e)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def get_current_price(self):
        try: return float(self.client.get_symbol_ticker(symbol=self.symbol)['price'])
        except Exception as e: 
            print(Fore.LIGHTRED_EX + str(e))
            subprocess.run(['python', TG_NOTIFICATOR_PATH, str(e)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def get_step_size(self):
        try: 
            return float(next(f for f in self.client.get_symbol_info(symbol=self.symbol)['filters'] if f['filterType'] == 'LOT_SIZE')['stepSize'])
        except Exception as e: 
            print(Fore.LIGHTRED_EX + str(e))
            subprocess.run(['python', TG_NOTIFICATOR_PATH, str(e)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    def buy(self, price, flc):
        self.buy_price = price
        #self.client.order_market_buy(symbol=self.symbol, quoteOrderQty=trading_sum)
        #self.coin_qty = float(self.client.get_asset_balance(asset=coin_input.upper())['free'])
        self.coin_qty = round(trading_sum / self.buy_price, 5)
        self.hold_crypto = True
        self.message = f"{selected_coin.split(' 👉')[0]}\nBuy 👉  {flc}%"
        subprocess.run(['python', TG_NOTIFICATOR_PATH, self.message], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def sell(self, price, flc):
        sell_qty = (self.coin_qty // self.coin_step) * self.coin_step
        #self.client.order_market_sell(symbol=self.symbol, quantity=sell_qty)
        profit = round((price - self.buy_price) * sell_qty, 2)
        self.hold_crypto = False
        self.buy_price = 0.0
        self.total_profit += profit
        self.message = f"{selected_coin.split(' 👉')[0]}\nSell 👉  {flc}%\nDeal profit 👉  {profit}$\nTotal profit 👉  {self.total_profit}$"
        subprocess.run(['python', TG_NOTIFICATOR_PATH, self.message], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def run(self):
        while True:
            current_p = self.get_current_price()

            if self.counter_avg in upd_120_hours:
                self.coin_step = self.get_step_size()

            if self.counter_avg in upd_8_hours:
                avg_p = self.get_avg_price()

            if self.counter_avg == 0:
                self.message = f"{selected_coin}\nFluc 👉  {round((current_p / avg_p * 100) - 100, 2)}%"
                subprocess.run(['python', TG_NOTIFICATOR_PATH, self.message], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
            try: fluc = round((current_p / avg_p * 100) - 100, 2)
            except Exception as e:
                print(Fore.LIGHTRED_EX + str(e))
                subprocess.run(['python', TG_NOTIFICATOR_PATH, 'Check trader bot!!!'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                sleep(600)
                continue

            if fluc < -float(sys.argv[4]) / 2:
                self.message = f"{selected_coin.split(' 👉')[0]}\nDANGER ZONE  👉  {fluc}%"
                subprocess.run(['python', TG_NOTIFICATOR_PATH, self.message], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
          
            if not self.hold_crypto:
                if current_p <= avg_p * buy_threshold:
                    self.buy(current_p, fluc)

            else: 
                if current_p >= self.buy_price * take_profit:
                    self.sell(current_p, fluc)

                elif current_p <= self.buy_price * stop_loss:
                    self.sell(current_p, fluc)
            
            sleep(60)
            self.counter_avg += 1

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Provide a coin name!!!")
        sys.exit()

    coin_input = sys.argv[1]
    bot = StableTrader(coin_input)
    
    try: bot.run()
    except KeyboardInterrupt: print('\n Stopped by user!!!')

