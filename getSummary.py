import os
import sqlite3
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from the .env file
load_dotenv()

# Now you can access API_KEY_GEMINI
api_key = os.getenv("API_KEY_GEMINI")
genai.configure(api_key=api_key)

# Connect to SQLite database and fetch the last 100 messages
def get_last_100_messages():
    conn = sqlite3.connect('bot_messages.db')  # Update with your database path if needed
    cursor = conn.cursor()
    
    # Fetch the last 100 messages, including username, date, and message_content
    cursor.execute("""
        SELECT username, date, message_content
        FROM messages
        ORDER BY date DESC
        LIMIT 100
    """)
    
    messages = cursor.fetchall()
    conn.close()
    
    return messages

# Format messages into plain text (conversation log format)
def format_messages_as_text(messages):
    return "\n".join([f"[{date}] {username}: {message}" for username, date, message in messages])

# Fetch and format the last 100 messages
messages = get_last_100_messages()
message_block = format_messages_as_text(messages)

# Create the model configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Create the model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

# Start a conversation
chat_session = model.start_chat()

# Send the message block and get a summary
response = chat_session.send_message(f"Summarize the following conversation: \n{message_block}")

# Output the summary
print("Summary: ", response.text)
