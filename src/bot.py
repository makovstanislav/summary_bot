import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from handlers import command_handlers, message_handlers, callback_handlers
from config import TG_TOKEN
from db.db_manager import setup_database

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    # Ensure TG_TOKEN is set
    if not TG_TOKEN:
        logger.error("Bot token not found in environment variables.")
        return
    
    # Set up the database
    setup_database()

    # Set up the application
    application = ApplicationBuilder().token(TG_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", command_handlers.start))
    application.add_handler(CommandHandler("help", command_handlers.help_command))
    application.add_handler(MessageHandler(filters.CONTACT, message_handlers.handle_contact))
    application.add_handler(MessageHandler(filters.TEXT & (filters.ChatType.GROUP | filters.ChatType.SUPERGROUP), message_handlers.handle_message))

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()
