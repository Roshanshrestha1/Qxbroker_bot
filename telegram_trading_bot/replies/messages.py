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
SETTINGS_BUTTON = "⚙️ Settings"
MANUAL_ANALYSIS_BUTTON = "📝 Manual Analysis"

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

# Settings messages
SETTINGS_TITLE = "⚙️ **Settings**\n\n"
SETTINGS_DEFAULT_TIMEFRAME = "Default Chart Timeframe: {timeframe}"
SETTINGS_DEFAULT_TRADE_TIME = "Default Trade Time: {trade_time}"
SETTINGS_SELECT_TIMEFRAME = "Select chart timeframe:"
SETTINGS_SELECT_TRADE_TIME = "Select trade expiration time:"
TIMEFRAME_SAVED = "✅ Chart timeframe set to *{timeframe}*"
TRADE_TIME_SAVED = "✅ Trade time set to *{trade_time}*"
SETTINGS_RESET = "✅ Settings reset to defaults"

# Manual Analysis messages
MANUAL_ANALYSIS_TITLE = "📝 **Manual Analysis**\n\n"
SELECT_TIMEFRAME = "Select chart timeframe for analysis:"
SELECT_TRADE_TIME = "Select trade expiration time:"
MANUAL_ANALYSIS_PROMPT = "Choose an asset and timeframe for manual analysis:"

# AI Analysis with timeframe messages
AI_ANALYSIS_WITH_TIMEFRAME = "🔍 Analyzing markets for {timeframe} chart... Please wait."
AI_BEST_TRADE_WITH_TIMEFRAME = """🎯 **Best Trade Opportunity**

💹 **{asset_name}** ({symbol})

{signal_emoji} **Signal:** {signal}
⏱️ **Chart Timeframe:** {timeframe}
⏳ **Trade Time:** {trade_time}
📊 **Confidence:** {confidence_text}

💰 **Current Price:** ${price}
📉 **RSI:** {rsi}
📈 **SMA(20):** ${sma}

📝 **Reason:** {reason}
{footer}"""

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
