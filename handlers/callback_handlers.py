"""Asset detail and callback handlers - Now supports analyze_asset_ callbacks."""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.market_data import get_ai_analysis, get_asset_category
from utils.telegram_helpers import create_main_menu_keyboard
from replies.messages import FOOTER_TEXT
from utils.logger import logger
from handlers.settings_handler import load_user_settings
from config import AVAILABLE_TIMEFRAMES, AVAILABLE_TRADE_TIMES


async def analyze_asset_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle detailed AI analysis for a specific asset clicked from Top 10 list.
    Callback format: analyze_asset_SYMBOL
    """
    query = update.callback_query
    await query.answer()
    
    # Extract symbol from callback data (e.g., "analyze_asset_BTCUSD=X")
    parts = query.data.split("_", 2)
    if len(parts) < 3:
        logger.error(f"Invalid callback data: {query.data}")
        return
    
    symbol = parts[2]
    logger.info(f"Detailed AI analysis requested for: {symbol} by user {update.effective_user.id}")
    
    # Load user settings for chart and trade time
    user_settings = load_user_settings(update.effective_user.id)
    chart_tf = user_settings.get('chart_timeframe', '5m')
    trade_tf = user_settings.get('trade_time', '5m')
    
    # Show loading message
    await query.edit_message_text(
        text=f"🤖 **AI is analyzing {symbol.replace('=X', '').replace('^', '')}...**\n\n"
             f"📊 Chart: {AVAILABLE_TIMEFRAMES.get(chart_tf, chart_tf)}\n"
             f"⏱️ Trade Time: {AVAILABLE_TRADE_TIMES.get(trade_tf, trade_tf)}\n\n"
             "⏳ *Please wait...*",
        parse_mode='Markdown'
    )
    
    try:
        # Get AI analysis
        analysis_text, signal = get_ai_analysis(symbol, chart_tf, trade_tf)
        
        if not analysis_text:
            await query.edit_message_text(
                text=f"❌ Failed to analyze {symbol}. Please try again.{FOOTER_TEXT}",
                reply_markup=create_main_menu_keyboard(),
                parse_mode='Markdown'
            )
            return
        
        # Add buttons for actions
        keyboard = [
            [InlineKeyboardButton("🔄 Re-Analyze", callback_data=f"analyze_asset_{symbol}")],
            [InlineKeyboardButton("🔙 Back to Top 10", callback_data="ai_trade_finder")],
            [InlineKeyboardButton("🏠 Return to Home", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=analysis_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        logger.info(f"AI analysis sent for {symbol}: {signal}")
        
    except Exception as e:
        logger.error(f"Error in AI analysis for {symbol}: {e}")
        await query.edit_message_text(
            text=f"❌ Error analyzing {symbol}.{FOOTER_TEXT}",
            reply_markup=create_main_menu_keyboard(),
            parse_mode='Markdown'
        )


async def asset_detail_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle asset button click.
    
    Fetches and displays detailed asset information.
    """
    query = update.callback_query
    await query.answer()
    
    # Extract category and symbol from callback data (e.g., "asset_crypto_BTCUSDT")
    parts = query.data.split("_", 2)
    if len(parts) < 3:
        logger.error(f"Invalid callback data: {query.data}")
        return
    
    category = parts[1]
    symbol = parts[2]
    
    logger.info(f"Asset detail requested: {symbol} ({category}) by user {update.effective_user.id}")
    
    # Show loading message
    await query.edit_message_text(
        text="📊 Loading data...",
    )
    
    try:
        from utils.market_data import fetch_data, calculate_rsi
        df = fetch_data(symbol, timeframe='5m', period='1d')
        
        if df is None or df.empty:
            await query.edit_message_text(
                text=f"❌ Data unavailable for {symbol}.{FOOTER_TEXT}",
                reply_markup=create_main_menu_keyboard(),
                parse_mode='Markdown'
            )
            return
        
        current_price = df['Close'].iloc[-1]
        rsi = calculate_rsi(df).iloc[-1]
        
        message = (
            f"📊 **{symbol.replace('=X', '').replace('^', '')}**\n\n"
            f"💰 Price: {current_price:.5f}\n"
            f"📉 RSI: {rsi:.2f}\n\n"
            f"{FOOTER_TEXT}"
        )
        
        keyboard = [
            [InlineKeyboardButton("🔙 Back", callback_data="ai_trade_finder")],
            [InlineKeyboardButton("🏠 Home", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        logger.info(f"Asset detail sent: {symbol}")
        
    except Exception as e:
        logger.error(f"Error fetching asset detail for {symbol}: {e}")
        await query.edit_message_text(
            text=f"❌ Error loading data.{FOOTER_TEXT}",
            reply_markup=create_main_menu_keyboard(),
            parse_mode='Markdown'
        )


async def refresh_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle refresh button click - redirects to AI trade finder.
    """
    query = update.callback_query
    await query.answer()
    
    logger.info("Refresh requested - redirecting to AI Trade Finder")
    
    # Redirect to AI trade finder
    from handlers.ai_trade_finder import ai_trade_finder_callback
    await ai_trade_finder_callback(update, context)


async def back_to_categories_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle back to categories button.
    """
    query = update.callback_query
    await query.answer()
    
    logger.info("Back to categories requested")
    
    from utils.telegram_helpers import create_category_keyboard
    from replies.messages import SELECT_CATEGORY
    
    message = f"{SELECT_CATEGORY}{FOOTER_TEXT}"
    
    await query.edit_message_text(
        text=message,
        reply_markup=create_category_keyboard(),
        parse_mode='Markdown'
    )


async def back_to_assets_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle back to assets list for a specific category.
    """
    # This is handled by trading_inside.asset_list_callback
    pass


async def back_to_main_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle back to main menu button.
    """
    from handlers.start_handler import start_command
    
    query = update.callback_query
    await query.answer()
    
    logger.info("Back to main menu requested")
    
    # Create a fake message object to reuse start_command
    class FakeMessage:
        def __init__(self, chat):
            self.chat = chat
    
    class FakeUpdate:
        def __init__(self, user, chat):
            self.effective_user = user
            self.message = FakeMessage(chat)
    
    fake_update = FakeUpdate(
        user=query.from_user,
        chat=query.message.chat
    )
    
    await start_command(fake_update, context)
