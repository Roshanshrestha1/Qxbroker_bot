"""Handler for /start command."""

from telegram import Update
from telegram.ext import ContextTypes
from utils.telegram_helpers import create_main_menu_keyboard
from replies.messages import START_MESSAGE, FOOTER_TEXT
from utils.logger import logger


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /start command.
    
    Shows welcome message with main menu buttons.
    """
    logger.info(f"Start command from user {update.effective_user.id}")
    
    # Create welcome message
    message = f"{START_MESSAGE}{FOOTER_TEXT}"
    
    # Get keyboard
    reply_markup = create_main_menu_keyboard()
    
    # Send message
    await update.message.reply_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
