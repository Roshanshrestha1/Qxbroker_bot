"""AI Best Trade Finder handler."""

from telegram import Update
from telegram.ext import ContextTypes
from utils.market_data import scan_assets_for_best_trade
from utils.telegram_helpers import (
    format_price,
    get_asset_display_name,
    create_main_menu_keyboard,
)
from replies.messages import (
    AI_ANALYZING,
    AI_NO_SIGNAL,
    AI_BEST_TRADE_TITLE,
    AI_CONFIDENCE_HIGH,
    AI_CONFIDENCE_MEDIUM,
    AI_CONFIDENCE_LOW,
    FOOTER_TEXT,
)
from utils.logger import logger
from assets.asset_lists import ALL_ASSETS


async def ai_trade_finder_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle AI Best Trade Finder button click.
    
    Scans multiple assets and returns the best trading opportunity.
    """
    logger.info(f"AI Trade Finder triggered by user {update.effective_user.id}")
    
    # Acknowledge the callback
    query = update.callback_query
    await query.answer()
    
    # Send analyzing message
    await query.edit_message_text(
        text=AI_ANALYZING,
    )
    
    try:
        # Scan assets for best trade
        best_trade = await scan_assets_for_best_trade(ALL_ASSETS)
        
        if not best_trade or best_trade.get('signal') == 'WAIT':
            # No strong signal found
            await query.edit_message_text(
                text=f"{AI_NO_SIGNAL}{FOOTER_TEXT}",
                reply_markup=create_main_menu_keyboard(),
                parse_mode='Markdown'
            )
            return
        
        # Build response message
        symbol = best_trade['symbol']
        asset_name = get_asset_display_name(symbol)
        signal = best_trade['signal']
        confidence = best_trade['confidence']
        reason = best_trade['reason']
        price = format_price(best_trade['price'])
        rsi = best_trade.get('rsi', 'N/A')
        sma = format_price(best_trade.get('sma'))
        
        # Signal emoji
        signal_emoji = "🟢" if signal == "BUY" else "🔴"
        
        # Confidence text
        confidence_map = {
            'HIGH': AI_CONFIDENCE_HIGH,
            'MEDIUM': AI_CONFIDENCE_MEDIUM,
            'LOW': AI_CONFIDENCE_LOW,
        }
        confidence_text = confidence_map.get(confidence, "")
        
        message = f"""{AI_BEST_TRADE_TITLE}
💹 **{asset_name}** ({symbol})

{signal_emoji} **Signal: {signal}**
📊 **Confidence:** {confidence_text}

💰 **Current Price:** ${price}
📉 **RSI:** {rsi}
📈 **SMA(20):** ${sma}

📝 **Reason:** {reason}
{FOOTER_TEXT}"""
        
        # Send result with main menu keyboard
        await query.edit_message_text(
            text=message,
            reply_markup=create_main_menu_keyboard(),
            parse_mode='Markdown'
        )
        
        logger.info(f"Best trade found: {symbol} - {signal} ({confidence})")
        
    except Exception as e:
        logger.error(f"Error in AI Trade Finder: {e}")
        await query.edit_message_text(
            text=f"❌ Error analyzing markets. Please try again.{FOOTER_TEXT}",
            reply_markup=create_main_menu_keyboard(),
            parse_mode='Markdown'
        )
