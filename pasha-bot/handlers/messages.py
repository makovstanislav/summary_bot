import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from db.db_manager import fetch_last_n_messages, insert_message  # Import the correct functions
from config import GEMINI_API_KEY
import google.generativeai as genai

# Load the Gemini API key from the .env file
genai.configure(api_key=GEMINI_API_KEY)

# Conversation states for getting user input
ASK_MESSAGE_COUNT = 1

# Function to call the Gemini API for a summary
def get_gemini_summary(prompt: str) -> str:
    # Define the model configuration
    generation_config = {
        "temperature": 1,
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
    await update.message.reply_text("How many messages do you want to summarize?")
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
            await update.message.reply_text("Please enter a positive number.")
            return ASK_MESSAGE_COUNT

        # Fetch the last N messages from the database
        logging.info(f"Fetching the last {message_count} messages from the database")
        messages = fetch_last_n_messages(message_count)
        logging.info(f"Fetched messages: {messages}")
        
        # Check if any messages were fetched
        if not messages:
            await update.message.reply_text(f"No messages found to summarize.")
            return ConversationHandler.END

        message_block = format_messages(messages)
        # Now we use it in the prompt
        prompt = (
            "Please summarize the following conversations grouped by threadID (sub-chats), ranked by the percentage of total messages for each thread, with threads sorted in descending order. "
            "Ensure the summary is concise, with a maximum of 2 bullet points per thread and no more than 10 words per bullet point.\n"
            
            "For each thread, use this format:\n\n"
            
            "🔵 Thread [threadID] – [percentage of total messages]% (whole number)\n"
            "  • [Key event or discussion point 1].\n"
            "  • [Key event or discussion point 2].\n\n"
            
            "Ensure the summary captures only the essential facts, prioritizing clarity and brevity, and round the percentages to whole numbers."
            
            f"Conversations:\n\n{message_block}"
        )
        
        logging.info(f"Generated prompt for Gemini API: {prompt}")

        # Call the Gemini API and get the summary
        summary = get_gemini_summary(prompt)
        logging.info(f"Received summary from Gemini API: {summary}")

        # Send the summary back to the user
        await update.message.reply_text(f"Here's what happened:\n\n{summary}")
        
        return ConversationHandler.END
    except ValueError:
        # Log the ValueError to help debug the issue
        logging.error(f"Invalid input for number of messages: {update.message.text}")
        # Handle invalid input (non-numeric values)
        await update.message.reply_text("Please enter a valid number.")
        return ASK_MESSAGE_COUNT
    except Exception as e:
        # Log any other errors that might occur
        logging.error(f"An error occurred: {str(e)}")
        await update.message.reply_text("An error occurred while processing your request. Please try again.")
        return ConversationHandler.END

# Format the last N messages into plain text, grouped by thread_id
def format_messages(messages):
    formatted_messages = []
    
    try:
        # Group messages by thread_id
        grouped_messages = {}
        for thread_id, username, date, message_content in messages:
            if thread_id not in grouped_messages:
                grouped_messages[thread_id] = []
            grouped_messages[thread_id].append((username, date, message_content))
        
        # Format messages for each thread
        for thread_id, msgs in grouped_messages.items():
            formatted_messages.append(f"- Thread: {thread_id}")
            for username, date, message_content in msgs:
                logging.info(f"Formatting message: {username}, {date}, {message_content}")
                formatted_messages.append(f"  - [{date}] {username}: {message_content}")
            formatted_messages.append("")  # Add a blank line between threads
    except Exception as e:
        logging.error(f"Error formatting messages: {str(e)}")
        raise e  # Rethrow the exception after logging it
    
    return "\n".join(formatted_messages)

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

        # Insert the message into the SQLite database
        insert_message(message_id, date, username, message_text, thread_id)

        # Log for debugging purposes
        logging.info(f"Stored message from {username} (ID: {message_id}) in the database.")

