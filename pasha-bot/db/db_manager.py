import sqlite3
from config import DB_PATH

# Function to set up the database (create tables if not exist)
def setup_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create a table for storing messages
    cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        message_id INTEGER,
                        date TEXT,
                        username TEXT,
                        message_content TEXT,
                        thread_id INTEGER
                    )''')
    conn.commit()
    conn.close()

# Function to insert message data into the SQLite database
def insert_message(message_id, date, username, message_content, thread_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Insert message details into the table
    cursor.execute('''INSERT INTO messages (message_id, date, username, message_content, thread_id)
                      VALUES (?, ?, ?, ?, ?)''',
                   (message_id, date, username, message_content, thread_id))
    conn.commit()
    conn.close()

# Fetch the last N messages ordered by date
def fetch_last_n_messages(n):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Fetch the last N messages ordered by date, including thread_id = None
    cursor.execute("""
        SELECT thread_id, username, date, message_content
        FROM messages
        ORDER BY date DESC
        LIMIT ?
    """, (n,))

    messages = cursor.fetchall()
    conn.close()

    return messages

# Fetch messages within the given date range
def fetch_messages_by_date_range(start_time, end_time):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT thread_id, username, date, message_content
        FROM messages
        WHERE date BETWEEN ? AND ?
        ORDER BY date DESC
    """, (start_time.isoformat(), end_time.isoformat()))

    messages = cursor.fetchall()
    conn.close()

    return messages