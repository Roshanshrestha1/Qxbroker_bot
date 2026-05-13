"""Asset detail and callback handlers - Now supports analyze_asset_ callbacks."""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.data_manager import get_data_manager, DataUnavailableError
from utils.telegram_helpers import create_main_menu_keyboard
from replies.messages import FOOTER_TEXT, PRIMARY_FAIL_FALLBACK, DATA_SOURCE_STATUS_BACKUP, DATA_SOURCE_STATUS_PRIMARY
from utils.logger import logger
from handlers.settings_handler import load_user_settings
from config import AVAILABLE_TIMEFRAMES, AVAILABLE_TRADE_TIMES


# Track fallback notification state per user (in-memory for session)
_user_fallback_notified = {}


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

    # Get data manager and check fallback status
    dm = get_data_manager()
    user_id = str(update.effective_user.id)

    # Check if we need to notify about fallback
    should_notify_fallback = False
    if dm.has_fallback_occurred() and not _user_fallback_notified.get(user_id, False):
        should_notify_fallback = True
        _user_fallback_notified[user_id] = True

    source_status = DATA_SOURCE_STATUS_BACKUP if dm.has_fallback_occurred() else DATA_SOURCE_STATUS_PRIMARY

    # Show loading message with data source status
    await query.edit_message_text(
        text=f"🤖 **AI is analyzing {symbol.replace('=X', '').replace('^', '')}...**\n\n"
             f"{source_status}\n"
             f"📊 Chart: {AVAILABLE_TIMEFRAMES.get(chart_tf, chart_tf)}\n"
             f"⏱️ Trade Time: {AVAILABLE_TRADE_TIMES.get(trade_tf, trade_tf)}\n\n"
             "⏳ *Please wait...*",
        parse_mode='Markdown'
    )

    # Send fallback notification if needed
    if should_notify_fallback:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=PRIMARY_FAIL_FALLBACK,
            parse_mode='Markdown'
        )

    try:
        # Get AI analysis using DataManager
        analysis_text, signal = dm.get_ai_analysis(symbol, chart_tf, trade_tf)

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

    except DataUnavailableError as e:
        logger.error(f"Data unavailable in analyze_asset: {e}")
        await query.edit_message_text(
            text=f"❌ Market data temporarily unavailable. Please try again later.{FOOTER_TEXT}",
            reply_markup=create_main_menu_keyboard(),
            parse_mode='Markdown'
        )
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
        dm = get_data_manager()
        df = dm.get_candles(category, symbol, timeframe='5m', period='1d')
        
        if df is None or df.empty:
            await query.edit_message_text(
                text=f"❌ Data unavailable for {symbol}.{FOOTER_TEXT}",
                reply_markup=create_main_menu_keyboard(),
                parse_mode='Markdown'
            )
            return
        
        current_price = df['Close'].iloc[-1]
        rsi_val = df['Close'].pct_change().rolling(window=14).std().iloc[-1]
        
        message = (
            f"📊 **{symbol.replace('=X', '').replace('^', '')}**\n\n"
            f"💰 Price: {current_price:.5f}\n"
            f"📉 Volatility: {rsi_val:.4f}\n\n"
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
        
    except DataUnavailableError as e:
        logger.error(f"Data unavailable for {symbol}: {e}")
        await query.edit_message_text(
            text=f"❌ Data temporarily unavailable.{FOOTER_TEXT}",
            reply_markup=create_main_menu_keyboard(),
            parse_mode='Markdown'
        )
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
