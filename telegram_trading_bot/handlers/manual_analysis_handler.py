"""Manual Analysis handler - user selects asset, timeframe, and trade time."""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.market_data import analyze_asset
from utils.telegram_helpers import (
    format_price,
    get_asset_display_name,
    create_main_menu_keyboard,
)
from replies.messages import (
    MANUAL_ANALYSIS_TITLE,
    SELECT_TIMEFRAME,
    SELECT_TRADE_TIME,
    ASSET_DETAIL_TEMPLATE,
    RECOMMENDATION_BUY,
    RECOMMENDATION_SELL,
    RECOMMENDATION_WAIT,
    DATA_UNAVAILABLE,
    LOADING_DATA,
    FOOTER_TEXT,
)
from config import AVAILABLE_TIMEFRAMES, AVAILABLE_TRADE_TIMES
from utils.logger import logger
from assets.asset_lists import ALL_ASSETS, CATEGORY_NAMES


async def manual_analysis_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle Manual Analysis button click - shows category selection."""
    logger.info(f"Manual Analysis triggered by user {update.effective_user.id}")
    
    query = update.callback_query
    await query.answer()
    
    message = f"{MANUAL_ANALYSIS_TITLE}First, select a category:{FOOTER_TEXT}"
    
    # Create category keyboard with back to menu
    keyboard = [
        [InlineKeyboardButton(CATEGORY_NAMES['crypto'], callback_data="manual_category_crypto")],
        [InlineKeyboardButton(CATEGORY_NAMES['forex'], callback_data="manual_category_forex")],
        [InlineKeyboardButton(CATEGORY_NAMES['indices'], callback_data="manual_category_indices")],
        [InlineKeyboardButton(CATEGORY_NAMES['commodities'], callback_data="manual_category_commodities")],
        [InlineKeyboardButton("🏠 Back to Menu", callback_data="back_to_main")],
    ]
    
    await query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )


async def manual_category_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle category selection in manual analysis."""
    query = update.callback_query
    await query.answer()
    
    # Extract category from callback data
    category = query.data.replace("manual_category_", "")
    
    logger.info(f"Manual analysis category selected: {category} by user {update.effective_user.id}")
    
    # Get assets for this category
    assets = ALL_ASSETS.get(category, [])
    
    if not assets:
        await query.edit_message_text(
            text=f"⚠️ No assets found for this category.{FOOTER_TEXT}",
            reply_markup=create_main_menu_keyboard(),
            parse_mode='Markdown'
        )
        return
    
    # Build asset buttons
    keyboard = []
    row = []
    for symbol in assets[:10]:  # Limit to first 10
        display_name = get_asset_display_name(symbol)
        if len(display_name) > 20:
            display_name = display_name[:17] + "..."
        row.append(InlineKeyboardButton(display_name, callback_data=f"manual_asset_{category}_{symbol}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("↩️ Back to Categories", callback_data="manual_analysis")])
    keyboard.append([InlineKeyboardButton("🏠 Back to Menu", callback_data="back_to_main")])
    
    message = f"{MANUAL_ANALYSIS_TITLE}Select an asset from *{CATEGORY_NAMES.get(category, category)}*:{FOOTER_TEXT}"
    
    await query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )


async def manual_asset_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle asset selection in manual analysis - show timeframe options."""
    query = update.callback_query
    await query.answer()
    
    # Extract category and symbol from callback data
    parts = query.data.split("_", 3)
    if len(parts) < 4:
        logger.error(f"Invalid manual asset callback data: {query.data}")
        return
    
    category = parts[2]
    symbol = parts[3]
    
    logger.info(f"Manual analysis asset selected: {symbol} ({category}) by user {update.effective_user.id}")
    
    # Store the selected asset in user context for next step
    context.user_data['manual_analysis_asset'] = {
        'category': category,
        'symbol': symbol,
    }
    
    message = f"{SELECT_TIMEFRAME}{FOOTER_TEXT}"
    
    # Create timeframe buttons
    keyboard = []
    for tf_code, tf_name in AVAILABLE_TIMEFRAMES.items():
        keyboard.append([InlineKeyboardButton(tf_name, callback_data=f"manual_tf_{tf_code}")])
    
    keyboard.append([InlineKeyboardButton("↩️ Back to Assets", callback_data=f"manual_back_assets_{category}")])
    keyboard.append([InlineKeyboardButton("🏠 Back to Menu", callback_data="back_to_main")])
    
    await query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )


async def manual_timeframe_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle timeframe selection - show trade time options."""
    query = update.callback_query
    await query.answer()
    
    # Extract timeframe from callback data
    timeframe = query.data.replace("manual_tf_", "")
    
    if timeframe not in AVAILABLE_TIMEFRAMES:
        await query.answer("Invalid timeframe", show_alert=True)
        return
    
    # Get stored asset info
    asset_info = context.user_data.get('manual_analysis_asset')
    if not asset_info:
        await query.edit_message_text(
            text=f"⚠️ Session expired. Please start again.{FOOTER_TEXT}",
            reply_markup=create_main_menu_keyboard(),
            parse_mode='Markdown'
        )
        return
    
    # Store timeframe for next step
    context.user_data['manual_analysis_timeframe'] = timeframe
    
    message = f"{SELECT_TRADE_TIME}{FOOTER_TEXT}"
    
    # Create trade time buttons
    keyboard = []
    for tt_code, tt_name in AVAILABLE_TRADE_TIMES.items():
        keyboard.append([InlineKeyboardButton(tt_name, callback_data=f"manual_tt_{tt_code}")])
    
    keyboard.append([InlineKeyboardButton("↩️ Back to Timeframes", callback_data="manual_analysis")])
    keyboard.append([InlineKeyboardButton("🏠 Back to Menu", callback_data="back_to_main")])
    
    await query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )


async def manual_trade_time_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle trade time selection - perform analysis and show results."""
    query = update.callback_query
    await query.answer()
    
    # Extract trade time from callback data
    trade_time = query.data.replace("manual_tt_", "")
    
    if trade_time not in AVAILABLE_TRADE_TIMES:
        await query.answer("Invalid trade time", show_alert=True)
        return
    
    # Get stored asset info and timeframe
    asset_info = context.user_data.get('manual_analysis_asset')
    timeframe = context.user_data.get('manual_analysis_timeframe')
    
    if not asset_info or not timeframe:
        await query.edit_message_text(
            text=f"⚠️ Session expired. Please start again.{FOOTER_TEXT}",
            reply_markup=create_main_menu_keyboard(),
            parse_mode='Markdown'
        )
        return
    
    category = asset_info['category']
    symbol = asset_info['symbol']
    
    logger.info(f"Manual analysis: {symbol} - Timeframe: {timeframe}, Trade Time: {trade_time}")
    
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
                reply_markup=create_main_menu_keyboard(),
                parse_mode='Markdown'
            )
            return
        
        # Build response with timeframe and trade time
        asset_name = get_asset_display_name(symbol)
        price = format_price(data['price'])
        change_24h = f"{data['change_24h']:+.2f}" if data.get('change_24h') else "N/A"
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
        
        # Add timeframe and trade time info
        message = f"""{MANUAL_ANALYSIS_TITLE}💹 **{asset_name}** ({symbol})

⏱️ **Chart Timeframe:** {AVAILABLE_TIMEFRAMES[timeframe]}
⏳ **Trade Time:** {AVAILABLE_TRADE_TIMES[trade_time]}

💰 Price: ${price}
📊 24h Change: {change_24h}%

📉 **Technical Analysis:**
• RSI: {rsi}
• SMA(20): ${sma}
• Trend: {trend}

💡 **Recommendation:** {recommendation}
{FOOTER_TEXT}"""
        
        # Keyboard with refresh and back options
        keyboard = [
            [
                InlineKeyboardButton("🔄 New Analysis", callback_data="manual_analysis"),
                InlineKeyboardButton("↩️ Back to Assets", callback_data=f"manual_back_assets_{category}"),
            ],
            [InlineKeyboardButton("🏠 Back to Menu", callback_data="back_to_main")],
        ]
        
        await query.edit_message_text(
            text=message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        
        logger.info(f"Manual analysis completed: {symbol}")
        
    except Exception as e:
        logger.error(f"Error in manual analysis for {symbol}: {e}")
        await query.edit_message_text(
            text=f"{DATA_UNAVAILABLE}{FOOTER_TEXT}",
            reply_markup=create_main_menu_keyboard(),
            parse_mode='Markdown'
        )
    
    # Clean up user data
    context.user_data.pop('manual_analysis_asset', None)
    context.user_data.pop('manual_analysis_timeframe', None)


async def manual_back_assets_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle back to assets list in manual analysis."""
    query = update.callback_query
    await query.answer()
    
    # Extract category from callback data
    category = query.data.replace("manual_back_assets_", "")
    
    # Get assets for this category
    assets = ALL_ASSETS.get(category, [])
    
    if not assets:
        await query.edit_message_text(
            text=f"⚠️ No assets found for this category.{FOOTER_TEXT}",
            reply_markup=create_main_menu_keyboard(),
            parse_mode='Markdown'
        )
        return
    
    # Build asset buttons
    keyboard = []
    row = []
    for symbol in assets[:10]:
        display_name = get_asset_display_name(symbol)
        if len(display_name) > 20:
            display_name = display_name[:17] + "..."
        row.append(InlineKeyboardButton(display_name, callback_data=f"manual_asset_{category}_{symbol}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("↩️ Back to Categories", callback_data="manual_analysis")])
    keyboard.append([InlineKeyboardButton("🏠 Back to Menu", callback_data="back_to_main")])
    
    message = f"{MANUAL_ANALYSIS_TITLE}Select an asset from *{CATEGORY_NAMES.get(category, category)}*:{FOOTER_TEXT}"
    
    await query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
