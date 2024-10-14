import logging
import os
import json
from datetime import datetime
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve the bot token from the environment variable
TG_TOKEN = os.getenv("TG_TOKEN")

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Function to handle the /start command
async def start(update: Update, context):
    user = update.effective_user
    username = user.username if user.username else user.first_name

    keyboard = [
        [KeyboardButton("Share your contact", request_contact=True)]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    await update.message.reply_text(f"Hello, {username}! Welcome to the bot.\nPlease share your phone number.", reply_markup=reply_markup)

# Function to handle contact sharing
async def handle_contact(update: Update, context):
    contact = update.message.contact
    phone_number = contact.phone_number

    user = update.effective_user
    username = user.username if user.username else user.first_name

    with open("user_data.log", "a") as file:
        file.write(f"User's Name: {username}, Phone Number: {phone_number}\n")

    await update.message.reply_text(f"Thank you! Your phone number is {phone_number}.")

# Function to handle all messages from the group and log in JSON format
async def handle_message(update: Update, context):
    if update.message and update.message.text:
        # Get message details
        message_id = update.message.message_id
        message_text = update.message.text
        date = update.message.date
        user = update.effective_user
        username = user.username if user.username else user.first_name

        # Get the thread ID if the message belongs to a thread (topic)
        thread_id = update.message.message_thread_id if update.message.is_topic_message else None

        # Create a dictionary to store the message details
        message_data = {
            "message_id": message_id,
            "date": date.isoformat(),  # Convert date to ISO format string
            "username": username,
            "message_content": message_text,  # Store message content in UTF-8
            "thread_id": thread_id  # Add thread ID if available
        }

        # Log the message data as a JSON object to a file in UTF-8 encoding
        with open("group_messages.json", "a", encoding='utf-8') as file:
            file.write(json.dumps(message_data, ensure_ascii=False) + "\n")  # Ensure UTF-8 storage

        # Log to the console for debugging
        logger.info(f"Logged message from {username} (Thread ID: {thread_id}): {message_text}")


# Function to handle the /help command
async def help_command(update: Update, context):
    await update.message.reply_text("Available commands:\n/start - Start the bot\n/help - Get help")

# Main function to set up and run the bot
def main():
    if not TG_TOKEN:
        logging.error("Bot token not found in .env file")
        return

    application = ApplicationBuilder().token(TG_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    application.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    application.add_handler(MessageHandler(filters.TEXT & (filters.ChatType.GROUP | filters.ChatType.SUPERGROUP), handle_message))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
