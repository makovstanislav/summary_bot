from telegram import KeyboardButton, ReplyKeyboardMarkup

def main_menu():
    buttons = [[KeyboardButton("History")], [KeyboardButton("Settings")]]
    return ReplyKeyboardMarkup(buttons, one_time_keyboard=True)
