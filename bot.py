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
# Import new handlers
from handlers.settings_handler import (
    settings_callback,
    settings_timeframe_callback,
    settings_trade_time_callback,
    set_timeframe_callback,
    set_trade_time_callback,
    settings_reset_callback,
)
from handlers.manual_analysis_handler import (
    manual_analysis_callback,
    manual_category_callback,
    manual_asset_callback,
    manual_timeframe_callback,
    manual_trade_time_callback,
    manual_back_assets_callback,
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
    application.add_handler(CallbackQueryHandler(manual_analysis_callback, pattern="^manual_analysis$"))
    application.add_handler(CallbackQueryHandler(settings_callback, pattern="^settings$"))
    
    # Settings handlers
    application.add_handler(CallbackQueryHandler(settings_timeframe_callback, pattern="^settings_timeframe$"))
    application.add_handler(CallbackQueryHandler(settings_trade_time_callback, pattern="^settings_trade_time$"))
    application.add_handler(CallbackQueryHandler(set_timeframe_callback, pattern="^set_timeframe_"))
    application.add_handler(CallbackQueryHandler(set_trade_time_callback, pattern="^set_trade_time_"))
    application.add_handler(CallbackQueryHandler(settings_reset_callback, pattern="^settings_reset$"))
    
    # Manual Analysis handlers
    application.add_handler(CallbackQueryHandler(manual_category_callback, pattern="^manual_category_"))
    application.add_handler(CallbackQueryHandler(manual_asset_callback, pattern="^manual_asset_"))
    application.add_handler(CallbackQueryHandler(manual_timeframe_callback, pattern="^manual_tf_"))
    application.add_handler(CallbackQueryHandler(manual_trade_time_callback, pattern="^manual_tt_"))
    application.add_handler(CallbackQueryHandler(manual_back_assets_callback, pattern="^manual_back_assets_"))
    
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
