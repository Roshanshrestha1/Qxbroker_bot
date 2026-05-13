"""Main bot application file."""

import asyncio
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
)
from config import BOT_TOKEN
from utils.logger import logger
from handlers import (
    start_command,
    ai_trade_finder_callback,
    trading_inside_callback,
    category_callback,
    asset_list_callback,
    asset_detail_callback,
    back_to_main_callback,
    back_to_categories_callback,
    refresh_callback,
)


def create_application() -> Application:
    """
    Create and configure the bot application.
    
    Returns:
        Application: Configured telegram bot application
    """
    # Build application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    
    # Add callback query handlers
    # Main menu buttons
    application.add_handler(CallbackQueryHandler(ai_trade_finder_callback, pattern="^ai_trade_finder$"))
    application.add_handler(CallbackQueryHandler(trading_inside_callback, pattern="^trading_inside$"))
    
    # Category selection
    application.add_handler(CallbackQueryHandler(category_callback, pattern="^category_"))
    
    # Asset selection
    application.add_handler(CallbackQueryHandler(asset_detail_callback, pattern="^asset_"))
    
    # Navigation
    application.add_handler(CallbackQueryHandler(back_to_main_callback, pattern="^back_to_main$"))
    application.add_handler(CallbackQueryHandler(back_to_categories_callback, pattern="^back_to_categories$"))
    application.add_handler(CallbackQueryHandler(asset_list_callback, pattern="^back_to_assets_"))
    
    # Refresh
    application.add_handler(CallbackQueryHandler(refresh_callback, pattern="^refresh_"))
    
    return application


async def post_init(application: Application) -> None:
    """Post-initialization hook."""
    logger.info("Bot initialized successfully!")
    logger.info(f"Bot username: @{(await application.bot.get_me()).username}")


def main() -> None:
    """
    Start the bot.
    
    This function initializes the bot application and starts polling for updates.
    """
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN not found! Please set it in your .env file or environment variables.")
        print("❌ Error: BOT_TOKEN not found!")
        print("Please copy .env.example to .env and add your bot token.")
        print("Example: BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz")
        return
    
    logger.info("Starting Trading Bot...")
    
    # Create application
    app = create_application()
    
    # Set post_init hook
    app.post_init = post_init
    
    # Start the bot
    logger.info("Bot is running. Press Ctrl+C to stop.")
    print("✅ Bot is running! Press Ctrl+C to stop.")
    
    # Run until shutdown
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
