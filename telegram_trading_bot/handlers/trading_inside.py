"""Trading Inside handler - category and asset list views."""

from telegram import Update
from telegram.ext import ContextTypes
from utils.telegram_helpers import (
    create_category_keyboard,
    create_asset_list_keyboard,
    create_main_menu_keyboard,
)
from replies.messages import (
    SELECT_CATEGORY,
    SELECT_ASSET,
    FOOTER_TEXT,
)
from assets.asset_lists import ALL_ASSETS, CATEGORY_NAMES
from utils.logger import logger


async def trading_inside_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle Trading Inside button click.
    
    Shows category selection menu.
    """
    logger.info(f"Trading Inside triggered by user {update.effective_user.id}")
    
    query = update.callback_query
    await query.answer()
    
    message = f"{SELECT_CATEGORY}{FOOTER_TEXT}"
    
    await query.edit_message_text(
        text=message,
        reply_markup=create_category_keyboard(),
        parse_mode='Markdown'
    )


async def category_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle category selection.
    
    Shows list of assets in the selected category.
    """
    query = update.callback_query
    await query.answer()
    
    # Extract category from callback data (e.g., "category_crypto")
    category = query.data.replace("category_", "")
    
    logger.info(f"Category selected: {category} by user {update.effective_user.id}")
    
    # Get assets for this category
    assets = ALL_ASSETS.get(category, [])
    
    if not assets:
        await query.edit_message_text(
            text=f"⚠️ No assets found for this category.{FOOTER_TEXT}",
            reply_markup=create_category_keyboard(),
            parse_mode='Markdown'
        )
        return
    
    message = f"{SELECT_ASSET}\n\n*{CATEGORY_NAMES.get(category, category)}*{FOOTER_TEXT}"
    
    await query.edit_message_text(
        text=message,
        reply_markup=create_asset_list_keyboard(assets, category),
        parse_mode='Markdown'
    )


async def asset_list_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle back to assets list.
    
    Returns to the asset list for a specific category.
    """
    query = update.callback_query
    await query.answer()
    
    # Extract category from callback data (e.g., "back_to_assets_crypto")
    category = query.data.replace("back_to_assets_", "")
    
    logger.info(f"Back to assets for category: {category}")
    
    # Get assets for this category
    assets = ALL_ASSETS.get(category, [])
    
    if not assets:
        await query.edit_message_text(
            text=f"⚠️ No assets found for this category.{FOOTER_TEXT}",
            reply_markup=create_category_keyboard(),
            parse_mode='Markdown'
        )
        return
    
    message = f"{SELECT_ASSET}\n\n*{CATEGORY_NAMES.get(category, category)}*{FOOTER_TEXT}"
    
    await query.edit_message_text(
        text=message,
        reply_markup=create_asset_list_keyboard(assets, category),
        parse_mode='Markdown'
    )
