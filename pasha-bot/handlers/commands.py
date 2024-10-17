from telegram import Update
from keyboards.buttons import get_start_buttons

# Function to handle the /start command
async def start(update: Update, context):
    user = update.effective_user
    username = user.username if user.username else user.first_name

    # Use the buttons from the separate file
    reply_markup = get_start_buttons()

    await update.message.reply_text(
        f"Hello, {username}! Welcome to the bot.\n"
        "Please click '🚀 Get summary'.", 
        reply_markup=reply_markup
    )

# Function to handle the /help command
async def help_command(update: Update, context):
    await update.message.reply_text("Available commands:\n/start - Start the bot\n/help - Get help")
