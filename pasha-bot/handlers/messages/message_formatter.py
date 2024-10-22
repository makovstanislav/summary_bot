
import logging
from handlers.messages.constants import THREAD_MAPPING

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
            formatted_messages.append(f"Thread {thread_id}")
            for username, date, message_content in reversed(msgs):  # Reverse to get chronological order
                logging.info(f"Formatting message: {username}, {date}, {message_content}")
                formatted_messages.append(f"  - [{date}] {username}: {message_content}")
            formatted_messages.append("")  # Add a blank line between threads
    except Exception as e:
        logging.error(f"Error formatting messages: {str(e)}")
        raise e  # Rethrow the exception after logging it
        
    return "\n".join(formatted_messages)

def replace_thread_ids_with_names(summary):
    for thread_id, thread_name in THREAD_MAPPING.items():
        thread_id_str = f"Thread {thread_id}" if thread_id is not None else "Thread None"
        # Replace "Thread [thread_id]" with thread_name
        summary = summary.replace(thread_id_str, thread_name)
    return summary