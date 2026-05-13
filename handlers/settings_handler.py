"""Settings handler for user preferences."""

import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.telegram_helpers import create_main_menu_keyboard
from replies.messages import (
    SETTINGS_TITLE,
    SETTINGS_DEFAULT_TIMEFRAME,
    SETTINGS_DEFAULT_TRADE_TIME,
    SETTINGS_SELECT_TIMEFRAME,
    SETTINGS_SELECT_TRADE_TIME,
    TIMEFRAME_SAVED,
    TRADE_TIME_SAVED,
    SETTINGS_RESET,
    FOOTER_TEXT,
)
from config import (
    DEFAULT_CHART_TIMEFRAME,
    DEFAULT_TRADE_TIME,
    AVAILABLE_TIMEFRAMES,
    AVAILABLE_TRADE_TIMES,
)
from utils.logger import logger

# Settings file path
SETTINGS_FILE = "data/user_settings.json"


def load_user_settings(user_id: int) -> dict:
    """Load settings for a specific user."""
    if not os.path.exists(SETTINGS_FILE):
        return {
            "chart_timeframe": DEFAULT_CHART_TIMEFRAME,
            "trade_time": DEFAULT_TRADE_TIME,
        }
    
    try:
        with open(SETTINGS_FILE, 'r') as f:
            all_settings = json.load(f)
            return all_settings.get(str(user_id), {
                "chart_timeframe": DEFAULT_CHART_TIMEFRAME,
                "trade_time": DEFAULT_TRADE_TIME,
            })
    except (json.JSONDecodeError, IOError):
        return {
            "chart_timeframe": DEFAULT_CHART_TIMEFRAME,
            "trade_time": DEFAULT_TRADE_TIME,
        }


def save_user_settings(user_id: int, settings: dict) -> None:
    """Save settings for a specific user."""
    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
    
    # Load all settings
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                all_settings = json.load(f)
        except (json.JSONDecodeError, IOError):
            all_settings = {}
    else:
        all_settings = {}
    
    # Update user settings
    all_settings[str(user_id)] = settings
    
    # Save back to file
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(all_settings, f, indent=2)


async def settings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle Settings button click."""
    logger.info(f"Settings triggered by user {update.effective_user.id}")
    
    query = update.callback_query
    await query.answer()
    
    # Load user settings
    user_settings = load_user_settings(update.effective_user.id)
    
    # Build settings display message
    message = f"""{SETTINGS_TITLE}
📊 {SETTINGS_DEFAULT_TIMEFRAME.format(timeframe=AVAILABLE_TIMEFRAMES.get(user_settings['chart_timeframe'], user_settings['chart_timeframe']))}
⏱️ {SETTINGS_DEFAULT_TRADE_TIME.format(trade_time=AVAILABLE_TRADE_TIMES.get(user_settings['trade_time'], user_settings['trade_time']))}

Choose an option:{FOOTER_TEXT}"""
    
    # Create settings keyboard
    keyboard = [
        [InlineKeyboardButton("📊 Chart Timeframe", callback_data="settings_timeframe")],
        [InlineKeyboardButton("⏱️ Trade Time", callback_data="settings_trade_time")],
        [InlineKeyboardButton("🔄 Reset to Defaults", callback_data="settings_reset")],
        [InlineKeyboardButton("🏠 Back to Menu", callback_data="back_to_main")],
    ]
    
    await query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )


async def settings_timeframe_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle chart timeframe selection in settings."""
    query = update.callback_query
    await query.answer()
    
    logger.info(f"Timeframe selection requested by user {update.effective_user.id}")
    
    message = f"{SETTINGS_SELECT_TIMEFRAME}{FOOTER_TEXT}"
    
    # Create timeframe buttons
    keyboard = []
    for tf_code, tf_name in AVAILABLE_TIMEFRAMES.items():
        keyboard.append([InlineKeyboardButton(tf_name, callback_data=f"set_timeframe_{tf_code}")])
    
    keyboard.append([InlineKeyboardButton("↩️ Back to Settings", callback_data="settings")])
    
    await query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )


async def settings_trade_time_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle trade time selection in settings."""
    query = update.callback_query
    await query.answer()
    
    logger.info(f"Trade time selection requested by user {update.effective_user.id}")
    
    message = f"{SETTINGS_SELECT_TRADE_TIME}{FOOTER_TEXT}"
    
    # Create trade time buttons
    keyboard = []
    for tt_code, tt_name in AVAILABLE_TRADE_TIMES.items():
        keyboard.append([InlineKeyboardButton(tt_name, callback_data=f"set_trade_time_{tt_code}")])
    
    keyboard.append([InlineKeyboardButton("↩️ Back to Settings", callback_data="settings")])
    
    await query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )


async def set_timeframe_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle setting a specific timeframe."""
    query = update.callback_query
    await query.answer()
    
    # Extract timeframe from callback data
    timeframe = query.data.replace("set_timeframe_", "")
    
    if timeframe not in AVAILABLE_TIMEFRAMES:
        await query.answer("Invalid timeframe", show_alert=True)
        return
    
    # Load and update settings
    user_settings = load_user_settings(update.effective_user.id)
    user_settings['chart_timeframe'] = timeframe
    save_user_settings(update.effective_user.id, user_settings)
    
    logger.info(f"User {update.effective_user.id} set timeframe to {timeframe}")
    
    message = TIMEFRAME_SAVED.format(timeframe=AVAILABLE_TIMEFRAMES[timeframe]) + FOOTER_TEXT
    
    # Back to settings keyboard
    keyboard = [
        [InlineKeyboardButton("↩️ Back to Settings", callback_data="settings")],
        [InlineKeyboardButton("🏠 Back to Menu", callback_data="back_to_main")],
    ]
    
    await query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )


async def set_trade_time_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle setting a specific trade time."""
    query = update.callback_query
    await query.answer()
    
    # Extract trade time from callback data
    trade_time = query.data.replace("set_trade_time_", "")
    
    if trade_time not in AVAILABLE_TRADE_TIMES:
        await query.answer("Invalid trade time", show_alert=True)
        return
    
    # Load and update settings
    user_settings = load_user_settings(update.effective_user.id)
    user_settings['trade_time'] = trade_time
    save_user_settings(update.effective_user.id, user_settings)
    
    logger.info(f"User {update.effective_user.id} set trade time to {trade_time}")
    
    message = TRADE_TIME_SAVED.format(trade_time=AVAILABLE_TRADE_TIMES[trade_time]) + FOOTER_TEXT
    
    # Back to settings keyboard
    keyboard = [
        [InlineKeyboardButton("↩️ Back to Settings", callback_data="settings")],
        [InlineKeyboardButton("🏠 Back to Menu", callback_data="back_to_main")],
    ]
    
    await query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )


async def settings_reset_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle reset settings to defaults."""
    query = update.callback_query
    await query.answer()
    
    # Reset to defaults
    default_settings = {
        "chart_timeframe": DEFAULT_CHART_TIMEFRAME,
        "trade_time": DEFAULT_TRADE_TIME,
    }
    save_user_settings(update.effective_user.id, default_settings)
    
    logger.info(f"User {update.effective_user.id} reset settings to defaults")
    
    message = SETTINGS_RESET + FOOTER_TEXT
    
    # Back to settings keyboard
    keyboard = [
        [InlineKeyboardButton("↩️ Back to Settings", callback_data="settings")],
        [InlineKeyboardButton("🏠 Back to Menu", callback_data="back_to_main")],
    ]
    
    await query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
