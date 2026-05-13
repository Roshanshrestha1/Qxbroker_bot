# Trading Bot with AI Analysis & Manual Analysis

A Telegram trading bot that provides AI-powered trade analysis and manual asset analysis with customizable timeframes.

## Features

### 🔍 AI Best Trade Finder
- Automatically scans multiple assets across crypto, forex, indices, and commodities
- Uses technical indicators (RSI, SMA) to find the best trading opportunities
- Provides exact chart timeframe and trade time based on your settings
- Shows confidence level and reasoning for each signal

### 📊 Trading Inside
- Browse assets by category (Crypto, Forex, Indices, Commodities)
- View detailed analysis for each asset
- Real-time price data from TradingView-compatible sources (Binance, Yahoo Finance)

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

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create `.env` file with your bot token:
   ```
   BOT_TOKEN=your_telegram_bot_token_here
   ```
4. Run the bot:
   ```bash
   python bot.py
   ```

## Data Sources
- **Crypto**: Binance (via ccxt)
- **Forex/Indices/Commodities**: Yahoo Finance

All data is fetched from reliable TradingView-compatible sources.

## Technical Indicators
- RSI (Relative Strength Index) - Period: 14
- SMA (Simple Moving Average) - Period: 20
- Trend detection based on price vs SMA

## Disclaimer
This bot is for informational purposes only. It does not provide financial advice. Trade at your own risk.
