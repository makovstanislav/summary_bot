import sqlite3
from config import DB_PATH

def setup_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            message TEXT
        )
    ''')
    conn.commit()
    conn.close()

def get_user_messages(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT message FROM messages WHERE user_id=?", (user_id,))
    messages = cursor.fetchall()
    conn.close()
    return [{"text": msg[0]} for msg in messages]
