import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from db.db_manager import fetch_last_n_messages, insert_message  # Import the correct functions
from config import GEMINI_API_KEY
import google.generativeai as genai

# --- Static Mapping for thread_id to thread_name ---
THREAD_MAPPING = {
    14133: "🚀 Паша-бот",
    14909: "❓ Вопросник",
    15982: "😄 Дофамин",
    16988: "🕺 MusicOnly",
    17191: "🏆 Run, POCO, run!",
    14115: "💃 Встречи",
    19276: "🌐 Network",
    17862: "🌀 Рабство вечное ?",
    18223: "📚 Читальный зал",
    14122: "👩🏻‍💻 ИТ помощь",
    None: "☕️ Женераль"
}

# Function to get thread_name from thread_id
def get_thread_name(thread_id):
    return THREAD_MAPPING.get(thread_id, f"Thread {thread_id}")  # Default to thread_id if no name is found

# Load the Gemini API key from the .env file
genai.configure(api_key=GEMINI_API_KEY)

# Conversation states for getting user input
ASK_MESSAGE_COUNT = 1

# Function to call the Gemini API for a summary
def get_gemini_summary(prompt: str) -> str:
    # Define the model configuration
    generation_config = {
        "temperature": 0,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    try:
        # Log before making the API request
        logging.info(f"Sending prompt to Gemini API: {prompt}")

        # Create the model
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config,
        )

        # Start a conversation and send the prompt
        chat_session = model.start_chat()
        response = chat_session.send_message(f"{prompt}")

        logging.info(f"Received response from Gemini API: {response}")

        return response.text if response else "No response from the Gemini API."
    except Exception as e:
        logging.error(f"Error in Gemini API call: {str(e)}")
        return "An error occurred while calling the Gemini API."

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
        
        message_block = format_messages(messages)
        prompt = (
            "Summarize the following conversations grouped by threadID (sub-chats), sort threads based on the volume of messages. "
            "Ensure the summary captures key facts, main topics, insights, or decisions made in each conversation, without excessive abstraction or redundancy. "
            "Focus on what was new, noteworthy, or decided during the discussion. Focus only on the most important threads, excluding trivial mentions. Limit the summary to no more than 1-3 bullet points per thread. "
            "Omit threads where messages lack meaningful content or reactions. If no significant interaction or follow-up occurred, omit the thread from the summary entirely. "
            "Make the summary engaging, concise, and useful, highlighting conclusions where possible. "
            "If there are no significant results or conclusions, do not force multiple bullet points—keep the summary minimal.\n"
            "The more descriptive you are about key topics covered, the better.\n"
            "Avoid redundancy or excessive length. Keep the report concise and focused on useful, noteworthy information.\n"
            "Your overall answer should be in Russian and should not exceed 2676 characters. Omit formatting.\n"
            "Don't repeat threads."
            
            "Here are some examples:\n\n"
                "🔵 Thread [thread_uid] \n"
                "  • Команда обсуждала улучшение навигации в приложении по управлению финансами. Решили объединить «Аналитику» и «Транзакции» на одном экране для удобства пользователей.\n"
                "  • A/B тестирование показало, что новая схема повысила конверсию на 20%, так что команда согласилась с идеей.\n\n"

                "🔵 Thread [thread_uid] \n"
                "  • Обсуждали редизайн сайта, чтобы ускорить загрузку страниц на мобильных устройствах. 30% пользователей жалуются на проблемы с доступом к разделу «Документы».\n"
                "  • Дизайнеры предложили упростить меню и провести тестирование с реальными пользователями, чтобы проверить новые прототипы.\n\n"

                "🔵 Thread [thread_uid] \n"
                "  • Ксения представила исследование по влиянию минималистичного дизайна на интернет-магазины: уменьшение визуальных элементов ускорило загрузку страниц на 35% и повысило конверсию на 12%.\n"
                "  • Команда согласилась применить этот подход в новом лендинге, оптимизировав графику и анимации.\n\n"

                "🔵 Thread [thread_uid] \n"
                "  • Алексей предложил перейти на AWS, чтобы сократить затраты на инфраструктуру на 40 000 долларов в год.\n"
                "  • Команда обсудила возможные риски и запустила пилотный проект для проверки совместимости баз данных.\n\n"

                "🔵 Thread [thread_uid] \n"
                "  • Анна сообщила, что время обработки заявок в новой версии CRM сократилось с 15 до 10 минут. Однако выявлены баги в аналитике продаж.\n"
                "  • Решили отложить внедрение обновлений, пока не устранят баги и не завершат дополнительное тестирование.\n\n"
            f"Conversations:\n\n{message_block}"
        )
        
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

# Format the last N messages into plain text, grouped by thread_id
def format_messages(messages):
    formatted_messages = []
    
    try:
        # Group messages by thread_id
        grouped_messages = {}
        for thread_id, username, date, message_content in messages:
            # Use thread_id as is, including None
            if thread_id not in grouped_messages:
                grouped_messages[thread_id] = []
            grouped_messages[thread_id].append((username, date, message_content))
        
        # Sort threads by the number of messages (optional)
        sorted_threads = sorted(grouped_messages.items(), key=lambda x: len(x[1]), reverse=True)
        
        # Format messages for each thread using thread_id
        for thread_id, msgs in sorted_threads:
            formatted_messages.append(f"🔵 Thread {thread_id}")
            for username, date, message_content in reversed(msgs):  # Reverse to get chronological order
                logging.info(f"Formatting message: {username}, {date}, {message_content}")
                formatted_messages.append(f"  - [{date}] {username}: {message_content}")
            formatted_messages.append("")  # Add a blank line between threads
    except Exception as e:
        logging.error(f"Error formatting messages: {str(e)}")
        raise e  # Rethrow the exception after logging it
        
    return "\n".join(formatted_messages)

# Function to replace thread_ids with thread_names in the summary
def replace_thread_ids_with_names(summary):
    for thread_id, thread_name in THREAD_MAPPING.items():
        thread_id_str = f"Thread {thread_id}" if thread_id is not None else "Thread None"
        # Replace "Thread [thread_id]" with thread_name
        summary = summary.replace(thread_id_str, thread_name)
    return summary

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

        # Log for debugging purposes
        logging.info(f"Handling message from {username} (ID: {message_id}) in thread {thread_id}.")

        # Insert the message into the SQLite database
        insert_message(message_id, date, username, message_text, thread_id)

        # Log the successful storage
        logging.info(f"Stored message from {username} (ID: {message_id}) in the database.")