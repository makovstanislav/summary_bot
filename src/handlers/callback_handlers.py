from telegram import Update
from telegram.ext import CallbackContext

async def button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(f"You clicked: {query.data}")
