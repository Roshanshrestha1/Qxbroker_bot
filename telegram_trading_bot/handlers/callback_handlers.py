"""Asset detail and callback handlers."""

from telegram import Update
from telegram.ext import ContextTypes
from utils.market_data import analyze_asset
from utils.telegram_helpers import (
    format_price,
    format_volume,
    get_asset_display_name,
    create_asset_detail_keyboard,
    create_category_keyboard,
    create_main_menu_keyboard,
)
from replies.messages import (
    ASSET_DETAIL_TEMPLATE,
    RECOMMENDATION_BUY,
    RECOMMENDATION_SELL,
    RECOMMENDATION_WAIT,
    DATA_UNAVAILABLE,
    LOADING_DATA,
    FOOTER_TEXT,
)
from utils.logger import logger


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
        text=LOADING_DATA,
    )
    
    try:
        # Analyze the asset
        data = await analyze_asset(symbol, category)
        
        if not data:
            await query.edit_message_text(
                text=f"{DATA_UNAVAILABLE}{FOOTER_TEXT}",
                reply_markup=create_asset_detail_keyboard(symbol, category),
                parse_mode='Markdown'
            )
            return
        
        # Build response
        asset_name = get_asset_display_name(symbol)
        price = format_price(data['price'])
        change_24h = f"{data['change_24h']:+.2f}" if data.get('change_24h') else "N/A"
        volume = format_volume(data.get('volume'))
        rsi = data.get('rsi', 'N/A')
        sma = format_price(data.get('sma'))
        trend = data.get('trend', 'Unknown')
        
        # Get recommendation based on signal
        signal = data.get('signal', 'WAIT')
        if signal == 'BUY':
            recommendation = RECOMMENDATION_BUY
        elif signal == 'SELL':
            recommendation = RECOMMENDATION_SELL
        else:
            recommendation = RECOMMENDATION_WAIT
        
        message = ASSET_DETAIL_TEMPLATE.format(
            asset_name=asset_name,
            symbol=symbol,
            price=price,
            change_24h=change_24h,
            volume=volume,
            rsi=rsi,
            sma=sma,
            trend=trend,
            recommendation=recommendation,
        ) + FOOTER_TEXT
        
        # Send with detail keyboard
        await query.edit_message_text(
            text=message,
            reply_markup=create_asset_detail_keyboard(symbol, category),
            parse_mode='Markdown'
        )
        
        logger.info(f"Asset detail sent: {symbol}")
        
    except Exception as e:
        logger.error(f"Error fetching asset detail for {symbol}: {e}")
        await query.edit_message_text(
            text=f"{DATA_UNAVAILABLE}{FOOTER_TEXT}",
            reply_markup=create_asset_detail_keyboard(symbol, category),
            parse_mode='Markdown'
        )


async def refresh_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle refresh button click.
    
    Reloads data for the same asset.
    """
    query = update.callback_query
    await query.answer()
    
    # Extract category and symbol from callback data (e.g., "refresh_crypto_BTCUSDT")
    parts = query.data.split("_", 2)
    if len(parts) < 3:
        logger.error(f"Invalid refresh callback data: {query.data}")
        return
    
    category = parts[1]
    symbol = parts[2]
    
    logger.info(f"Refresh requested for: {symbol}")
    
    # Reuse asset_detail_callback logic
    await query.edit_message_text(text=LOADING_DATA)
    
    try:
        data = await analyze_asset(symbol, category)
        
        if not data:
            await query.edit_message_text(
                text=f"{DATA_UNAVAILABLE}{FOOTER_TEXT}",
                reply_markup=create_asset_detail_keyboard(symbol, category),
                parse_mode='Markdown'
            )
            return
        
        asset_name = get_asset_display_name(symbol)
        price = format_price(data['price'])
        change_24h = f"{data['change_24h']:+.2f}" if data.get('change_24h') else "N/A"
        volume = format_volume(data.get('volume'))
        rsi = data.get('rsi', 'N/A')
        sma = format_price(data.get('sma'))
        trend = data.get('trend', 'Unknown')
        
        signal = data.get('signal', 'WAIT')
        if signal == 'BUY':
            recommendation = RECOMMENDATION_BUY
        elif signal == 'SELL':
            recommendation = RECOMMENDATION_SELL
        else:
            recommendation = RECOMMENDATION_WAIT
        
        message = ASSET_DETAIL_TEMPLATE.format(
            asset_name=asset_name,
            symbol=symbol,
            price=price,
            change_24h=change_24h,
            volume=volume,
            rsi=rsi,
            sma=sma,
            trend=trend,
            recommendation=recommendation,
        ) + FOOTER_TEXT
        
        await query.edit_message_text(
            text=message,
            reply_markup=create_asset_detail_keyboard(symbol, category),
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Error refreshing data for {symbol}: {e}")
        await query.edit_message_text(
            text=f"{DATA_UNAVAILABLE}{FOOTER_TEXT}",
            reply_markup=create_asset_detail_keyboard(symbol, category),
            parse_mode='Markdown'
        )


async def back_to_categories_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle back to categories button.
    """
    query = update.callback_query
    await query.answer()
    
    logger.info("Back to categories requested")
    
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
