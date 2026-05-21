# Binance Volatility Trading Bot

An automated trading suite that identifies high-potential coins and manages trade lifecycles based on volatility-weighted analysis.

## Architecture
- `coin.py`: Performs market scanning and strategy validation.
- `bnbot.py`: Executes buy/sell logic and monitors open positions.
- `tg_notificator.py`: Handles asynchronous Telegram notifications.

## Prerequisites
- Python 3.x
- Binance API Key & Secret
- Telegram API Credentials (App ID, Hash, Bot Token)
- A `.env` file for environment variable management

## Installation
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install python-binance telethon python-dotenv colorama numpy
   
Configure your .env file:

Code snippet:
    binance_api_key=your_key
    binance_api_secret=your_secret
    tg_bot_token=your_bot_token
    app_id=your_app_id
    app_hash=your_app_hash
    tg_user_id=your_telegram_id
    DOTENV_FILE_PATH=path/to/.env
    tg_notificator_path=path/to/notifier.py


## Usage

### 1. Analyzing Market Opportunities
To scan all USDT pairs and identify candidates meeting the volatility criteria:
```bash
python coin.py
2. Running the Trading Bot
To start the trader for a specific coin (e.g., BTC), define your thresholds (percent):

Bash
# Usage: python bnbot.py [COIN] [BUY_THRESHOLD] [TAKE_PROFIT] [STOP_LOSS]
python bnbot.py btc -2.0 5.0 -10.0
Strategy Logic
Filtering: Validates assets using quoteVolume thresholds and price percentage stability.

Decision Engine: Uses a combination of Volume-Weighted Averages (VWA) and Median price fluctuations to identify assets in a "Valid" state.

Trading: Employs a mean-reversion strategy. The bot enters a position when the price deviates significantly below the 8-hour average and exits upon reaching target profit or stop-loss limits.

Safety & Warnings
Experimental: This code is for educational purposes. Use with testnet accounts first. For real tradinf first uncomment binance method

API Security: Ensure your .env file is never uploaded to public repositories.

Error Handling: The system includes basic exception handling and Telegram alerts to notify you of API connection issues.
