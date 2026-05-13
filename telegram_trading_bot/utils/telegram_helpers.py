"""Telegram helper utilities."""

from typing import List, Tuple
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from assets.asset_lists import ASSET_NAMES, CATEGORY_NAMES


def format_price(price: float) -> str:
    """Format price based on its value."""
    if price is None:
        return "N/A"
    
    if price >= 1000:
        return f"{price:,.2f}"
    elif price >= 1:
        return f"{price:.4f}"
    else:
        return f"{price:.6f}"


def format_volume(volume: float) -> str:
    """Format volume with appropriate suffix."""
    if volume is None:
        return "N/A"
    
    if volume >= 1_000_000_000:
        return f"{volume / 1_000_000_000:.2f}B"
    elif volume >= 1_000_000:
        return f"{volume / 1_000_000:.2f}M"
    elif volume >= 1_000:
        return f"{volume / 1_000:.2f}K"
    else:
        return f"{volume:.2f}"


def get_asset_display_name(symbol: str) -> str:
    """Get friendly display name for an asset."""
    return ASSET_NAMES.get(symbol, symbol)


def create_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Create the main menu inline keyboard."""
    from replies.messages import AI_TRADE_FINDER_BUTTON, TRADING_INSIDE_BUTTON, SETTINGS_BUTTON, MANUAL_ANALYSIS_BUTTON
    
    keyboard = [
        [InlineKeyboardButton(AI_TRADE_FINDER_BUTTON, callback_data="ai_trade_finder")],
        [InlineKeyboardButton(TRADING_INSIDE_BUTTON, callback_data="trading_inside")],
        [InlineKeyboardButton(MANUAL_ANALYSIS_BUTTON, callback_data="manual_analysis")],
        [InlineKeyboardButton(SETTINGS_BUTTON, callback_data="settings")],
    ]
    return InlineKeyboardMarkup(keyboard)


def create_category_keyboard() -> InlineKeyboardMarkup:
    """Create category selection keyboard."""
    keyboard = [
        [InlineKeyboardButton(CATEGORY_NAMES['crypto'], callback_data="category_crypto")],
        [InlineKeyboardButton(CATEGORY_NAMES['forex'], callback_data="category_forex")],
        [InlineKeyboardButton(CATEGORY_NAMES['indices'], callback_data="category_indices")],
        [InlineKeyboardButton(CATEGORY_NAMES['commodities'], callback_data="category_commodities")],
        [InlineKeyboardButton("🏠 Back to Menu", callback_data="back_to_main")],
    ]
    return InlineKeyboardMarkup(keyboard)


def create_asset_list_keyboard(symbols: List[str], category: str) -> InlineKeyboardMarkup:
    """Create keyboard with asset buttons."""
    # Create buttons in rows of 2
    keyboard = []
    row = []
    
    for symbol in symbols:
        display_name = get_asset_display_name(symbol)
        # Truncate long names
        if len(display_name) > 20:
            display_name = display_name[:17] + "..."
        
        button = InlineKeyboardButton(
            f"{display_name}",
            callback_data=f"asset_{category}_{symbol}"
        )
        row.append(button)
        
        if len(row) == 2:
            keyboard.append(row)
            row = []
    
    if row:
        keyboard.append(row)
    
    # Add back button
    keyboard.append([InlineKeyboardButton("↩️ Back to Categories", callback_data="back_to_categories")])
    
    return InlineKeyboardMarkup(keyboard)


def create_asset_detail_keyboard(symbol: str, category: str) -> InlineKeyboardMarkup:
    """Create keyboard for asset detail view with Refresh and Back buttons."""
    keyboard = [
        [
            InlineKeyboardButton("🔄 Refresh", callback_data=f"refresh_{category}_{symbol}"),
            InlineKeyboardButton("↩️ Back to Assets", callback_data=f"back_to_assets_{category}"),
        ],
        [InlineKeyboardButton("🏠 Back to Menu", callback_data="back_to_main")],
    ]
    return InlineKeyboardMarkup(keyboard)


def create_back_to_main_keyboard() -> InlineKeyboardMarkup:
    """Create a simple back to main menu keyboard."""
    keyboard = [
        [InlineKeyboardButton("🏠 Back to Menu", callback_data="back_to_main")],
    ]
    return InlineKeyboardMarkup(keyboard)

