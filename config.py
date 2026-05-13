# Bot Configuration
import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Admin/User IDs (optional, for restricting access)
ADMIN_IDS = os.getenv("ADMIN_IDS", "").split(",") if os.getenv("ADMIN_IDS") else []

# TradingView webhook secret (optional, for validation)
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "default_secret")

# Exchange settings
BINANCE_RATE_LIMIT = 1.2  # seconds between requests to avoid rate limiting

# Analysis settings
RSI_PERIOD = 14
SMA_PERIOD = 20
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

# Default timeframes and trade times
DEFAULT_CHART_TIMEFRAME = "1h"
DEFAULT_TRADE_TIME = "5m"

# Available timeframes (TradingView compatible)
AVAILABLE_TIMEFRAMES = {
    "1m": "1 Minute",
    "5m": "5 Minutes",
    "15m": "15 Minutes",
    "30m": "30 Minutes",
    "1h": "1 Hour",
    "4h": "4 Hours",
    "1d": "1 Day",
}

# Available trade times (binary options style)
AVAILABLE_TRADE_TIMES = {
    "1m": "1 Minute",
    "2m": "2 Minutes",
    "5m": "5 Minutes",
    "10m": "10 Minutes",
    "15m": "15 Minutes",
    "30m": "30 Minutes",
    "1h": "1 Hour",
}

# Quotex/Broker specific timeframes
QUOTEX_TIMEFRAMES = {
    "turbo": "Turbo (1m)",
    "short": "Short (5m)",
    "medium": "Medium (15m)",
    "long": "Long (1h)",
}

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = "data/bot.log"
