"""AI Best Trade Finder handler - Scans ALL QX Broker assets and shows Top 10."""

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


async def ai_trade_finder_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle AI Best Trade Finder button click.
    Scans ALL QX Broker assets and returns TOP 10 best opportunities.
    """
    logger.info(f"AI Trade Finder triggered by user {update.effective_user.id}")
    
    query = update.callback_query
    await query.answer()
    
    # Load user settings
    user_settings = load_user_settings(update.effective_user.id)
    trade_time = user_settings.get('trade_time', '5m')
    chart_tf = user_settings.get('chart_timeframe', '5m')
    
    # Get data manager
    dm = get_data_manager()
    
    # Check if we need to notify about fallback
    user_id = str(update.effective_user.id)
    should_notify_fallback = False
    
    if dm.has_fallback_occurred() and not _user_fallback_notified.get(user_id, False):
        should_notify_fallback = True
        _user_fallback_notified[user_id] = True
    
    # Send analyzing message with data source status
    source_status = DATA_SOURCE_STATUS_BACKUP if dm.has_fallback_occurred() else DATA_SOURCE_STATUS_PRIMARY
    
    analyzing_text = (
        "🔍 **AI is scanning ALL QX Broker assets...**\n\n"
        f"{source_status}\n"
        "⏳ *Please wait while I analyze Forex, Crypto, Commodities, Indices & Stocks...*\n\n"
        f"📊 Chart Timeframe: {AVAILABLE_TIMEFRAMES.get(chart_tf, chart_tf)}\n"
        f"⏱️ Trade Duration: {AVAILABLE_TRADE_TIMES.get(trade_time, trade_time)}"
    )
    
    await query.edit_message_text(
        text=analyzing_text,
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
        # Scan ALL assets for top 10 opportunities
        top_assets = dm.scan_assets(limit=10)
        
        if not top_assets:
            await query.edit_message_text(
                text=f"❌ No strong trading opportunities found right now.{FOOTER_TEXT}",
                reply_markup=create_main_menu_keyboard(),
                parse_mode='Markdown'
            )
            return
        
        # Build Top 10 list with buttons
        message = "🏆 **TOP 10 BEST TRADING OPPORTUNITIES** 🏆\n\n"
        message += f"📊 Chart: {AVAILABLE_TIMEFRAMES.get(chart_tf, chart_tf)} | ⏱️ Trade: {AVAILABLE_TRADE_TIMES.get(trade_time, trade_time)}\n\n"
        message += "Based on AI analysis of RSI, Volatility & Trend Strength:\n\n"
        
        keyboard_buttons = []
        
        for i, asset in enumerate(top_assets, 1):
            symbol = asset['symbol']
            name = asset['name']
            signal = asset['signal']
            score = asset['score']
            rsi = asset['rsi']
            category = asset['category']
            source = asset.get('source', 'YAHOO')
            
            # Medal emoji for top 3
            if i == 1:
                medal = "🥇"
            elif i == 2:
                medal = "🥈"
            elif i == 3:
                medal = "🥉"
            else:
                medal = "🔹"
            
            signal_emoji = "🟢" if "CALL" in signal or "Buy" in signal else "🔴"
            
            # Show data source icon
            source_icon = "📊" if source == "TRADINGVIEW" else "💹"
            
            message += f"{medal} *#{i} - {name}* ({category}) {source_icon}\n"
            message += f"   Signal: {signal_emoji} {signal}\n"
            message += f"   Score: {score}/100 | RSI: {rsi:.1f}\n\n"
            
            # Add button for each asset (top 10 as inline buttons in rows)
            keyboard_buttons.append([
                InlineKeyboardButton(
                    f"{medal} #{i} {name} - {signal}", 
                    callback_data=f"analyze_asset_{symbol}"
                )
            ])
        
        message += f"👇 *Click any asset above for detailed AI analysis!*\n\n{FOOTER_TEXT}"
        
        # Add Return to Home button
        keyboard_buttons.append([InlineKeyboardButton("🏠 Return to Home", callback_data="main_menu")])
        
        reply_markup = InlineKeyboardMarkup(keyboard_buttons)
        
        await query.edit_message_text(
            text=message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        logger.info(f"Found {len(top_assets)} top trading opportunities")
        
    except DataUnavailableError as e:
        logger.error(f"Data unavailable in AI Trade Finder: {e}")
        await query.edit_message_text(
            text=f"❌ Market data temporarily unavailable. Please try again later.{FOOTER_TEXT}",
            reply_markup=create_main_menu_keyboard(),
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error in AI Trade Finder: {e}")
        await query.edit_message_text(
            text=f"❌ Error scanning markets. Please try again.{FOOTER_TEXT}",
            reply_markup=create_main_menu_keyboard(),
            parse_mode='Markdown'
        )
