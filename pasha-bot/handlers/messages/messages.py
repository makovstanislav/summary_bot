import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from db.db_manager import fetch_last_n_messages, insert_message
from config import GEMINI_API_KEY
from handlers.messages.prompt_builder import build_prompt
from handlers.messages.api_client import get_gemini_summary
from handlers.messages.message_formatter import format_messages, replace_thread_ids_with_names

# Conversation states for getting user input
ASK_MESSAGE_COUNT = 1

# Function to ask the user how many messages they want summarized
async def get_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Сколько сообщений вы хотите обобщить?")
    return ASK_MESSAGE_COUNT

# Function to process the number of messages and interact with the Gemini API
async def process_message_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Log the raw input
        logging.info(f"Received user input: {update.message.text}")
        
        # Try to parse the user input as an integer
        user_input = update.message.text.strip()  # Remove leading/trailing spaces
        message_count = int(user_input)  # Try to convert input to an integer
        
        # Log the parsed integer
        logging.info(f"Parsed integer: {message_count}")

        # Check if the number is positive
        if message_count <= 0:
            await update.message.reply_text("Пожалуйста, введите положительное число.")
            return ASK_MESSAGE_COUNT

        # Fetch the last N messages from the database
        logging.info(f"Fetching the last {message_count} messages from the database")
        messages = fetch_last_n_messages(message_count)
        logging.info(f"Fetched messages: {messages}")
        
        # Check if any messages were fetched
        if not messages:
            await update.message.reply_text(f"Сообщения для обобщения не найдены.")
            return ConversationHandler.END

        message_block = format_messages(messages)
        prompt = build_prompt(message_block)

        logging.info(f"Generated prompt for Gemini API: {prompt}")

        # Call the Gemini API and get the summary
        summary = get_gemini_summary(prompt)
        logging.info(f"Received summary from Gemini API: {summary}")

        # Replace thread_ids with thread_names in the summary
        summary = replace_thread_ids_with_names(summary)

        # Send the summary back to the user
        await update.message.reply_text(f"Ключевые обсуждения:\n\n{summary}")
        
        return ConversationHandler.END
    except ValueError:
        # Log the ValueError to help debug the issue
        logging.error(f"Invalid input for number of messages: {update.message.text}")
        # Handle invalid input (non-numeric values)
        await update.message.reply_text("Пожалуйста, введите действительное число.")
        return ASK_MESSAGE_COUNT
    except Exception as e:
        # Log any other errors that might occur
        logging.error(f"An error occurred: {str(e)}")
        await update.message.reply_text("Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте еще раз.")
        return ConversationHandler.END

# Function to handle all messages and store them in the database
# Function to handle all messages and store them in the database
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        # Capture message details
        message_id = update.message.message_id
        message_text = update.message.text
        date = update.message.date.isoformat()
        user = update.effective_user
        username = user.username if user.username else user.first_name
        thread_id = update.message.message_thread_id if update.message.is_topic_message else None
        chat_id = update.message.chat_id  # Add this line to capture chat_id

        # Log for debugging purposes
        logging.info(f"Handling message from {username} (ID: {message_id}) in thread {thread_id} and chat {chat_id}.")
        
        # Insert the message into the SQLite database
        insert_message(message_id, date, username, message_text, thread_id)

        # Log the successful storage
        logging.info(f"Stored message from {username} (ID: {message_id}) in the database.")