"""All reply messages for the bot."""

# Start message
START_MESSAGE = """
👋 Welcome to the **Trading Bot**!

I help you find the best trading opportunities using technical analysis.

Choose an option below:
"""

# Main menu buttons
AI_TRADE_FINDER_BUTTON = "🔍 AI Best Trade Finder"
TRADING_INSIDE_BUTTON = "📊 Trading Inside"

# AI Trade Finder messages
AI_ANALYZING = "🔍 Analyzing markets... Please wait."
AI_NO_SIGNAL = "❌ No strong signals found at the moment. Try again later."
AI_BEST_TRADE_TITLE = "🎯 **Best Trade Opportunity**\n\n"
AI_CONFIDENCE_HIGH = "🟢 High Confidence"
AI_CONFIDENCE_MEDIUM = "🟡 Medium Confidence"
AI_CONFIDENCE_LOW = "🔴 Low Confidence"

# Trading Inside messages
SELECT_CATEGORY = "📊 Select a category:"
SELECT_ASSET = "📈 Select an asset:"
DATA_UNAVAILABLE = "⚠️ Data temporarily unavailable. Try again later."
LOADING_DATA = "⏳ Fetching data..."

# Asset detail message template
ASSET_DETAIL_TEMPLATE = """
💹 **{asset_name}** ({symbol})

💰 Price: ${price}
📊 24h Change: {change_24h}%
📈 Volume: {volume}

📉 **Technical Analysis:**
• RSI: {rsi}
• SMA(20): ${sma}
• Trend: {trend}

💡 **Recommendation:** {recommendation}
"""

# Recommendation texts
RECOMMENDATION_BUY = "✅ Consider BUY"
RECOMMENDATION_SELL = "❌ Consider SELL"
RECOMMENDATION_WAIT = "⏸️ Wait / Hold"

# Button labels
REFRESH_BUTTON = "🔄 Refresh"
BACK_BUTTON = "↩️ Back to Assets"
BACK_TO_MAIN_BUTTON = "🏠 Back to Menu"

# Category buttons
CRYPTO_BUTTON = "🪙 Crypto"
FOREX_BUTTON = "💱 Forex"
INDICES_BUTTON = "📈 Indices"
COMMODITIES_BUTTON = "🏆 Commodities"

# Error messages
ERROR_GENERAL = "❌ An error occurred. Please try again."
ERROR_RATE_LIMIT = "⚠️ Rate limit reached. Please wait a moment."
ERROR_TIMEOUT = "⏱️ Request timed out. Try again."

# Footer text
FOOTER_TEXT = "\n\n⚠️ *Disclaimer: This is not financial advice. Trade at your own risk.*"
