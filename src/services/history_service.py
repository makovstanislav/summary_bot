from db.db_manager import get_user_messages

def get_user_history(user_id):
    messages = get_user_messages(user_id)
    return "\n".join([msg['text'] for msg in messages])
