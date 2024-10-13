import logging
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Function to handle the /start command
async def start(update: Update, context):
    # Get the user's username or fallback to their first name
    user = update.effective_user
    username = user.username if user.username else user.first_name

    # Create a button that requests the user's phone number
    keyboard = [
        [KeyboardButton("Share your contact", request_contact=True)]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    # Send a welcome message and request the phone number
    await update.message.reply_text(f"Hello, {username}! Welcome to the bot.\nPlease share your phone number.", reply_markup=reply_markup)

# Function to handle contact sharing
async def handle_contact(update: Update, context):
    # Get the user's contact information
    contact = update.message.contact
    phone_number = contact.phone_number

    # Get the user's name (username or first name)
    user = update.effective_user
    username = user.username if user.username else user.first_name

    # Log the username and phone number to a file
    with open("user_data.txt", "a") as file:
        file.write(f"User's Name: {username}, Phone Number: {phone_number}\n")

    # Respond with the user's phone number
    await update.message.reply_text(f"Thank you! Your phone number is {phone_number}.")

# Function to handle all messages from the group
async def handle_message(update: Update, context):
    # Get the message content and the user who sent it
    message_text = update.message.text
    user = update.effective_user
    username = user.username if user.username else user.first_name

    # Log the message to a file
    with open("group_messages.txt", "a") as file:
        file.write(f"{username}: {message_text}\n")

    # Optionally respond or process the message further
    # Example: await update.message.reply_text("Message received!")

# Function to handle the /help command
async def help_command(update: Update, context):
    # Send a help message when the user sends /help
    await update.message.reply_text("Available commands:\n/start - Start the bot\n/help - Get help")

# Main function to set up and run the bot
def main():
    # Create the bot with your API token
    application = ApplicationBuilder().token("TOKEN HEREs").build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # Add a handler for receiving the contact (phone number)
    application.add_handler(MessageHandler(filters.CONTACT, handle_contact))

    # Add a handler for receiving all text messages in the group
    application.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUP, handle_message))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()