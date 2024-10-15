from telegram import Update
from telegram.ext import CallbackContext

async def start(update: Update, context: CallbackContext):
    user = update.effective_user
    await update.message.reply_text(f"Hello, {user.first_name}! Welcome to the bot.")

async def help_command(update: Update, context: CallbackContext):
    await update.message.reply_text("Available commands:\n/start - Start the bot\n/help - Get help")
