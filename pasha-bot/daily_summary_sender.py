import logging
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from pytz import timezone
from telegram import Bot
from config import TG_TOKEN, DAILY_SUMMARY_CHAT_ID
from db.db_manager import fetch_messages_by_date_range
from handlers.messages.prompt_builder import build_prompt
from handlers.messages.message_formatter import format_messages
from handlers.messages.api_client import get_gemini_summary
import asyncio

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize the bot
bot = Bot(token=TG_TOKEN)

# Define the timezone
LOCAL_TZ = timezone('Europe/Zurich')  # Set your local timezone (example for Switzerland)

# Define the async function to fetch and send daily summary
async def send_daily_summary():
    try:
        # Get the current time and the time 24 hours ago
        end_time = datetime.datetime.now(LOCAL_TZ)
        start_time = end_time - datetime.timedelta(hours=24)

        # Fetch messages from the last 24 hours
        messages = fetch_messages_by_date_range(start_time, end_time)

        # Format the messages into a block and build the prompt
        message_block = format_messages(messages)
        prompt = build_prompt(message_block)

        # Get the summary from the Gemini API
        summary = get_gemini_summary(prompt)

        # Send the summary to the Daily Summaries chat in a specific thread
        await bot.send_message(
            chat_id=DAILY_SUMMARY_CHAT_ID,
            text=f"📋 Ежедневное саммари:\n\n{summary}",
            message_thread_id="20284"
        )
        logger.info("Successfully sent the daily summary")
    
    except Exception as e:
        logger.error(f"Failed to send daily summary: {str(e)}")

# Wrapper to run async function inside the synchronous APScheduler
def run_async_task():
    asyncio.run(send_daily_summary())

# Set up the scheduler to run the task at 11:30 AM every day
scheduler = BlockingScheduler(timezone=LOCAL_TZ)
scheduler.add_job(run_async_task, 'cron', hour=1, minute=53)

# Start the scheduler
if __name__ == "__main__":
    logger.info("Starting the daily summary scheduler")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped.")
        
# python daily_summary_sender.py