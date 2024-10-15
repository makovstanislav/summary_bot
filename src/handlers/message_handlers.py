from telegram import Update
from telegram.ext import CallbackContext
from services.history_service import get_user_history
from services.gemini_service import GeminiService
from config import GEMINI_API_KEY

# Function to handle user contact sharing
async def handle_contact(update: Update, context: CallbackContext):
    contact = update.message.contact
    phone_number = contact.phone_number

    user = update.effective_user
    username = user.username if user.username else user.first_name

    # Log or store the user's contact details
    with open("user_data.log", "a") as file:
        file.write(f"User's Name: {username}, Phone Number: {phone_number}\n")

    # Reply to the user
    await update.message.reply_text(f"Thank you, {username}! Your phone number is {phone_number}.")

async def handle_message(update: Update, context: CallbackContext):
    user_message = update.message.text
    user_history = get_user_history(update.effective_user.id)
    gemini_service = GeminiService(GEMINI_API_KEY)
    gemini_response = gemini_service.get_custom_response(user_message)
    
    await update.message.reply_text(f"History:\n{user_history}\n\nGemini says: {gemini_response}")
