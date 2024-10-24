import os
from dotenv import load_dotenv

load_dotenv()

TG_TOKEN = os.getenv("TG_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DB_PATH = os.getenv("DB_PATH", "db/bot_messages.db")  # Fallback to default if not set
DAILY_SUMMARY_CHAT_ID = "-1002261651604"
