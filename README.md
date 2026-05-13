# Trading Bot with AI Analysis & Manual Analysis

A Telegram trading bot that provides AI-powered trade analysis and manual asset analysis with customizable timeframes. **Now integrated with QX Broker as primary data source with automatic fallback to Yahoo Finance/Binance.**

## Features

### 🔍 AI Best Trade Finder
- Automatically scans multiple assets across crypto, forex, indices, and commodities
- Uses technical indicators (RSI, SMA) to find the best trading opportunities
- Provides exact chart timeframe and trade time based on your settings
- Shows confidence level and reasoning for each signal

### 📊 Trading Inside
- Browse assets by category (Crypto, Forex, Indices, Commodities)
- View detailed analysis for each asset
- Real-time price data from **QX Broker** (primary) or TradingView-compatible sources (Binance, Yahoo Finance) as fallback

### 📝 Manual Analysis
- Select any asset manually
- Choose your preferred chart timeframe (1m, 5m, 15m, 30m, 1h, 4h, 1d)
- Choose your trade expiration time (1m, 2m, 5m, 10m, 15m, 30m, 1h)
- Get detailed technical analysis with recommendations

### ⚙️ Settings
- Set default chart timeframe for AI analysis
- Set default trade time for all analyses
- Reset to defaults anytime
- Settings are saved per user

### 🏠 Navigation
- All screens have "Back to Menu" button
- Easy navigation between categories and assets
- Return to home from anywhere

### 🔄 Automatic Fallback System
- **Primary Source**: QX Broker (via API-Quotex with Playwright authentication)
- **Fallback Source**: Yahoo Finance / Binance
- Automatically switches to fallback if QX Broker is unavailable
- Periodically attempts to reconnect to QX Broker every 5 minutes
- Notifies users when fallback activates or recovers

## Timeframes Available

### Chart Timeframes (TradingView compatible)
- 1 Minute
- 5 Minutes
- 15 Minutes
- 30 Minutes
- 1 Hour
- 4 Hours
- 1 Day

### Trade Times (Binary Options style)
- 1 Minute
- 2 Minutes
- 5 Minutes
- 10 Minutes
- 15 Minutes
- 30 Minutes
- 1 Hour

## Installation

### Quick Start (Recommended)
Run the setup script which will guide you through configuration:
```bash
chmod +x run.sh
./run.sh
```

The script will:
1. Create a virtual environment
2. Install all dependencies including Playwright browsers
3. Ask for your Telegram Bot Token
4. Ask for your QX Broker credentials (email/password)
5. Start the bot

### Manual Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   python -m playwright install chromium
   ```
3. Create `.env` file with your credentials:
   ```
   # Telegram Bot Token
   BOT_TOKEN=your_telegram_bot_token_here
   
   # QX Broker Credentials (Primary Data Source)
   QX_EMAIL=your_qx_broker_email@example.com
   QX_PASSWORD=your_qx_broker_password
   
   # Primary data source: "qxbroker" or "yfinance"
   PRIMARY_DATA_SOURCE=qxbroker
   
   # Optional: Connection timeout (seconds)
   QX_TIMEOUT=5
   ```
4. Run the bot:
   ```bash
   python bot.py
   ```

## First Run - Browser Authentication

On the first run, the bot will open a Chromium browser window to authenticate with QX Broker and extract the SSID token. This is required only once - subsequent runs will reuse the stored session.

**Steps:**
1. Bot starts and opens browser automatically
2. Complete the QX Broker login in the browser
3. Close the browser after successful login
4. Bot continues running with authenticated session

## Data Sources

### Primary: QX Broker
- Real-time WebSocket data via API-Quotex
- Supports all QX Broker assets (Forex, Crypto, Commodities, Stocks, Indices)
- Uses Playwright for secure authentication
- GitHub: https://github.com/A11ksa/API-Quotex

### Fallback: Yahoo Finance / Binance
- Automatically activated if QX Broker is unavailable
- Crypto: Binance (via ccxt)
- Forex/Indices/Commodities: Yahoo Finance

## Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `BOT_TOKEN` | Telegram Bot Token | Required |
| `QX_EMAIL` | QX Broker email | Required for QX |
| `QX_PASSWORD` | QX Broker password | Required for QX |
| `PRIMARY_DATA_SOURCE` | "qxbroker" or "yfinance" | "qxbroker" |
| `QX_TIMEOUT` | Connection timeout (seconds) | 5 |
| `SIMULATE_QX_FAILURE` | Test fallback mode | False |

### Testing Fallback Mode
To test the fallback system without QX Broker credentials:
```
PRIMARY_DATA_SOURCE=yfinance
```

Or simulate QX failure while keeping credentials:
```
SIMULATE_QX_FAILURE=True
```

## Technical Indicators
- RSI (Relative Strength Index) - Period: 14
- SMA (Simple Moving Average) - Period: 20
- Trend detection based on price vs SMA

## Supported Assets (QX Broker)
The bot works exclusively with assets available in your QX Broker account:
- **Forex**: EUR/USD, GBP/USD, USD/JPY, etc. (including OTC pairs)
- **Crypto**: Bitcoin, Ethereum, Ripple, etc. (OTC)
- **Commodities**: Gold, Silver, US Crude, UK Brent
- **Stocks**: Apple, Microsoft, Tesla, etc. (OTC)
- **Indices**: S&P 500, NASDAQ, FTSE 100, etc.

## Troubleshooting

### Browser doesn't open on first run
```bash
python -m playwright install chromium
```

### QX Broker authentication fails
- Delete `sessions/session.json` and restart
- Ensure your QX Broker credentials are correct
- Check if QX Broker is accessible in your region

### Fallback activated unexpectedly
- Check logs for connection errors
- Verify QX Broker credentials in `.env`
- Ensure stable internet connection

## Disclaimer
This bot is for informational purposes only. It does not provide financial advice. Trade at your own risk.

## Credits
- **API-Quotex**: https://github.com/A11ksa/API-Quotex
- **Playwright**: https://playwright.dev/
- **python-telegram-bot**: https://python-telegram-bot.org/
