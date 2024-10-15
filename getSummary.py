import os
import sqlite3
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from the .env file
load_dotenv()

# Now you can access API_KEY_GEMINI
api_key = os.getenv("API_KEY_GEMINI")
genai.configure(api_key=api_key)

# Connect to SQLite database and fetch the last 100 messages grouped by thread_id
def get_messages_grouped_by_thread():
    conn = sqlite3.connect('bot_messages.db')  # Update with your database path if needed
    cursor = conn.cursor()
    
    # Fetch messages grouped by thread_id
    cursor.execute("""
        SELECT thread_id, username, date, message_content
        FROM messages
        ORDER BY thread_id, date DESC
        LIMIT 1000
    """)
    
    messages = cursor.fetchall()
    conn.close()
    
    # Group messages by thread_id
    grouped_messages = {}
    for thread_id, username, date, message in messages:
        if thread_id not in grouped_messages:
            grouped_messages[thread_id] = []
        grouped_messages[thread_id].append(f"[{date}] {username}: {message}")
    
    return grouped_messages

# Format the grouped messages into plain text for each thread
def format_messages_by_thread(grouped_messages):
    formatted_threads = []
    
    for thread_id, messages in grouped_messages.items():
        message_block = "\n".join(messages)
        formatted_threads.append(f"Thread {thread_id}:\n{message_block}\n")
    
    return "\n".join(formatted_threads)

# Fetch and format the messages by thread
grouped_messages = get_messages_grouped_by_thread()
message_block = format_messages_by_thread(grouped_messages)

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

# Send the grouped messages to Gemini API and ask for a structured summary
response = chat_session.send_message(f"Please summarize the following conversations, grouped by thread (topics):\n\n{message_block}")

# Output the summary
print("Summary: ", response.text)
