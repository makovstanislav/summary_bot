from telegram import KeyboardButton, ReplyKeyboardMarkup

def get_start_buttons():
    """Returns the buttons for the /start command."""
    buttons = [
        [KeyboardButton("🚀 Get summary")],  # Add an emoji as an "icon"
    ]
    return ReplyKeyboardMarkup(buttons, one_time_keyboard=True)

