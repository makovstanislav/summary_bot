# constants.py

# --- Static Mapping for thread_id to thread_name ---
THREAD_MAPPING = {
    14133: "🚀 Паша-бот",
    14909: "❓ Вопросник",
    15982: "😄 Дофамин",
    16988: "🕺 MusicOnly",
    17191: "🏆 Run, POCO, run!",
    14115: "💃 Встречи",
    19276: "🌐 Network",
    17862: "🌀 Рабство вечное ?",
    18223: "📚 Читальный зал",
    14122: "👩🏻‍💻 ИТ помощь",
    None: "☕️ Женераль"
}

# Function to get thread_name from thread_id
def get_thread_name(thread_id):
    return THREAD_MAPPING.get(thread_id, f"Thread {thread_id}")  # Default to thread_id if no name is found