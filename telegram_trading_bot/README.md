# 🤖 Telegram Trading Bot

A production-ready Telegram bot for trading analysis with AI-powered trade suggestions and real-time market data.

## 📋 Features

### 1. **AI Best Trade Finder**
- Scans top assets across Crypto, Forex, Indices, and Commodities
- Uses RSI + SMA technical indicators
- Returns the best BUY/SELL opportunity with confidence score
- Shows detailed reasoning for each recommendation

### 2. **Trading Inside**
- Browse assets by category:
  - 🪙 **Crypto**: BTC, ETH, SOL, XRP, ADA, DOGE, etc.
  - 💱 **Forex**: EUR/USD, GBP/USD, USD/JPY, etc.
  - 📈 **Indices**: S&P 500, NASDAQ, Dow Jones, etc.
  - 🏆 **Commodities**: Gold, Silver, Oil, Natural Gas, etc.
- Real-time price data with 24h change
- Technical analysis (RSI, SMA, Trend)
- Buy/Sell/Hold recommendations
- Refresh button to update data

### 3. **Technical Indicators**
- **RSI (Relative Strength Index)**: Identifies overbought (>70) and oversold (<30) conditions
- **SMA (Simple Moving Average)**: 20-period trend indicator
- **Trading Logic**:
  - BUY: RSI < 30 AND Price > SMA
  - SELL: RSI > 70 AND Price < SMA

## 📁 Project Structure

```
telegram_trading_bot/
├── bot.py                  # Main application entry point
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── README.md              # This file
├── handlers/
│   ├── __init__.py
│   ├── start_handler.py       # /start command handler
│   ├── ai_trade_finder.py     # AI trade finder logic
│   ├── trading_inside.py      # Category and asset list views
│   └── callback_handlers.py   # Button click handlers
├── utils/
│   ├── __init__.py
│   ├── market_data.py         # Data fetching (Binance, Yahoo Finance)
│   ├── indicators.py          # Technical indicators (RSI, SMA)
│   ├── telegram_helpers.py    # Keyboard builders, formatters
│   └── logger.py              # Logging setup
├── assets/
│   ├── __init__.py
│   └── asset_lists.py         # Asset symbols and names
├── replies/
│   ├── __init__.py
│   └── messages.py            # All bot response texts
└── data/
    └── bot.log                # Log file (auto-created)
```

## 🚀 Quick Start

### Option 1: One-Command Setup (Recommended) ⭐

The easiest way to set up and run the bot is using the provided `run.sh` script:

```bash
cd telegram_trading_bot
chmod +x run.sh
./run.sh
```

This script will automatically:
1. ✅ Check Python installation
2. 📦 Create a virtual environment
3. 📥 Install all dependencies
4. 🔐 Ask you for your Bot Token interactively
5. 🚀 Start the bot immediately

**That's it!** Just paste your token when prompted, and the bot will start running.

---

### Option 2: Manual Setup

If you prefer to set up manually:

#### Step 1: Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 3: Configure Environment
```bash
cp .env.example .env
```

Edit `.env` and add your bot token:
```env
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
LOG_LEVEL=INFO
```

#### Step 4: Run the Bot
```bash
python bot.py
```

You should see:
```
✅ Bot is running! Press Ctrl+C to stop.
```

## 🤖 Getting Your Bot Token

1. Open Telegram and search for **@BotFather**
2. Send `/newbot` command
3. Follow the instructions:
   - Choose a name for your bot (e.g., "My Trading Bot")
   - Choose a username (must end in "bot", e.g., "my_trading_bot")
4. BotFather will give you a token like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`
5. Copy this token to your `.env` file

## 📱 Using the Bot

1. Open Telegram and find your bot
2. Send `/start` command
3. You'll see two buttons:
   - **🔍 AI Best Trade Finder**: Get the best trading opportunity
   - **📊 Trading Inside**: Browse assets by category

### Navigation Flow:
```
/start → Main Menu
   ├─→ AI Best Trade Finder → Best trade suggestion
   └─→ Trading Inside → Categories
         ├─→ Crypto → Asset list → Asset details
         ├─→ Forex → Asset list → Asset details
         ├─→ Indices → Asset list → Asset details
         └─→ Commodities → Asset list → Asset details
```

## 🌐 Deployment

### Deploy on Railway (Free)

1. Create a [Railway](https://railway.app/) account
2. Create a new project → "Deploy from GitHub repo"
3. Connect your repository
4. Add environment variable: `BOT_TOKEN`
5. Railway will auto-detect `requirements.txt` and deploy

### Deploy on Render (Free)

1. Create a [Render](https://render.com/) account
2. Create new "Web Service"
3. Connect your GitHub repository
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `python bot.py`
6. Add environment variable: `BOT_TOKEN`

### Deploy with Docker

Create a `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["python", "bot.py"]
```

Then run:
```bash
docker build -t trading-bot .
docker run -e BOT_TOKEN=your_token trading-bot
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `BOT_TOKEN` | Telegram bot token | Required |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | INFO |
| `ADMIN_IDS` | Comma-separated admin user IDs (optional) | "" |

### Customizing Assets

Edit `assets/asset_lists.py` to add/remove assets:

```python
CRYPTO_ASSETS = [
    "BTCUSDT",
    "ETHUSDT",
    "YOUR_SYMBOL_HERE",  # Add new assets here
]
```

### Customizing Messages

All bot messages are in `replies/messages.py`. Edit them to change:
- Welcome message
- Button labels
- Error messages
- Recommendation texts

## 🔧 Troubleshooting

### "BOT_TOKEN not found!"
- Make sure you created `.env` file from `.env.example`
- Check that `BOT_TOKEN` is set correctly (no quotes, no spaces)

### "Data temporarily unavailable"
- Network issue or API rate limit
- Wait a few seconds and try again
- Check logs in `data/bot.log`

### Bot doesn't respond
- Make sure bot is running (`python bot.py`)
- Check if you're using the correct bot token
- Verify the bot is not blocked

### Import errors
- Make sure you're in the `telegram_trading_bot` directory
- Run `pip install -r requirements.txt` again
- Check Python version (3.8+)

## 📊 Data Sources

- **Crypto**: Binance (via CCXT library) - Free public API
- **Forex/Indices/Commodities**: Yahoo Finance (via yfinance) - Free

No API keys required for basic usage!

## ⚠️ Disclaimer

This bot is for **educational and informational purposes only**. It does not provide financial advice. Always do your own research before making trading decisions. The developers are not responsible for any losses incurred from using this bot.

## 📝 License

MIT License - Feel free to use and modify for your projects.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## 📞 Support

For questions or issues:
1. Check the logs in `data/bot.log`
2. Review this README
3. Open an issue on GitHub

---

**Happy Trading! 📈**
