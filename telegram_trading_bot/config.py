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

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = "data/bot.log"
