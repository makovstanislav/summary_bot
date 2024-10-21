from apscheduler.schedulers.blocking import BlockingScheduler
import logging
import datetime

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define the task to be run at the scheduled time
def scheduled_task():
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"Task executed at {current_time}")
    # You can replace this with the logic to generate the summary from messages

# Create a scheduler instance
scheduler = BlockingScheduler()

# Schedule the task for 22:21 every day
scheduler.add_job(scheduled_task, 'cron', hour=22, minute=23)

# Start the scheduler
if __name__ == "__main__":
    logger.info("Starting the scheduler")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped.")