import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from db.db_manager import fetch_last_n_messages, insert_message  # Import the correct functions
from config import GEMINI_API_KEY
import google.generativeai as genai

# --- Static Mapping for thread_id to thread_name ---
THREAD_MAPPING = {
    14133: "👨‍💻 Паша-бот",
    14909: "❓ Вопросник",
    15982: "Дофамин",
    16988: "🕺 MusicOnly",
    17191: "🏆 Run, POCO, run!",
    14115: "💃 Встречи",
    19276: "☕️ Network",
    17862: "🌀 Рабство вечное ?",
    18223: "📚 Читальный зал",
    14122: "🖥️ ИТ помощь",
    None: "☀️ Женераль"
}

# Function to get thread_name from thread_id
def get_thread_name(thread_id):
    return THREAD_MAPPING.get(thread_id, f"Thread {thread_id}")  # Default to thread_id if no name is found

# Load the Gemini API key from the .env file
genai.configure(api_key=GEMINI_API_KEY)

# Conversation states for getting user input
ASK_MESSAGE_COUNT = 1

# Function to call the Gemini API for a summary
def get_gemini_summary(prompt: str) -> str:
    # Define the model configuration
    generation_config = {
        "temperature": 0,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    try:
        # Log before making the API request
        logging.info(f"Sending prompt to Gemini API: {prompt}")

        # Create the model
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config,
        )

        # Start a conversation and send the prompt
        chat_session = model.start_chat()
        response = chat_session.send_message(f"{prompt}")

        logging.info(f"Received response from Gemini API: {response}")

        return response.text if response else "No response from the Gemini API."
    except Exception as e:
        logging.error(f"Error in Gemini API call: {str(e)}")
        return "An error occurred while calling the Gemini API."

# Function to ask the user how many messages they want summarized
async def get_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("How many messages do you want to summarize?")
    return ASK_MESSAGE_COUNT

# Function to process the number of messages and interact with the Gemini API
async def process_message_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Log the raw input
        logging.info(f"Received user input: {update.message.text}")
        
        # Try to parse the user input as an integer
        user_input = update.message.text.strip()  # Remove leading/trailing spaces
        message_count = int(user_input)  # Try to convert input to an integer
        
        # Log the parsed integer
        logging.info(f"Parsed integer: {message_count}")

        # Check if the number is positive
        if message_count <= 0:
            await update.message.reply_text("Please enter a positive number.")
            return ASK_MESSAGE_COUNT

        # Fetch the last N messages from the database
        logging.info(f"Fetching the last {message_count} messages from the database")
        messages = fetch_last_n_messages(message_count)
        logging.info(f"Fetched messages: {messages}")
        
        # Check if any messages were fetched
        if not messages:
            await update.message.reply_text(f"No messages found to summarize.")
            return ConversationHandler.END

        message_block = format_messages(messages)
        prompt = (
            "Summarize the following conversations grouped by threadID (sub-chats), sort threads based on the volume of messages. "
            "Ensure the summary captures key facts, main topics, insights, or decisions made in each conversation, without excessive abstraction or redundancy. "
            "Focus on what was new, noteworthy, or decided during the discussion. Limit the summary to no more than 1-3 bullet points per thread. "
            "Make the summary engaging, concise, and useful, highlighting conclusions where possible. "
            "If there are no significant results or conclusions, do not force multiple bullet points—keep the summary minimal.\n"
            "The more descriptive you are about key topics covered, the better.\n"
            "Your answer should not exceed 2676 characters. Omit formatting.\n"
            
            "Here are some examples:\n\n"

           "🔵 Thread [thread_id] \n"
            "  • Команда обсуждала улучшение навигации в приложении по управлению финансами. Решили объединить «Аналитику» и «Транзакции» на одном экране для удобства пользователей.\n"
            "  • A/B тестирование показало, что новая схема повысила конверсию на 20%, так что команда согласилась с идеей.\n\n"
            
            "🔵 Thread [thread_id] \n"
            "  • Обсуждали редизайн сайта, чтобы ускорить загрузку страниц на мобильных устройствах. 30% пользователей жалуются на проблемы с доступом к разделу «Документы».\n"
            "  • Дизайнеры предложили упростить меню и провести тестирование с реальными пользователями, чтобы проверить новые прототипы.\n\n"
            
            "🔵 Thread [thread_id] \n"
            "  • Ксения представила исследование по влиянию минималистичного дизайна на интернет-магазины: уменьшение визуальных элементов ускорило загрузку страниц на 35% и повысило конверсию на 12%.\n"
            "  • Команда согласилась применить этот подход в новом лендинге, оптимизировав графику и анимации.\n\n"
            
            "🔵 Thread [thread_id] \n"
            "  • Алексей предложил перейти на AWS, чтобы сократить затраты на инфраструктуру на 40 000 долларов в год.\n"
            "  • Команда обсудила возможные риски и запустила пилотный проект для проверки совместимости баз данных.\n\n"
            
            "🔵 Thread [thread_id] \n"
            "  • Анна сообщила, что время обработки заявок в новой версии CRM сократилось с 15 до 10 минут. Однако выявлены баги в аналитике продаж.\n"
            "  • Решили отложить внедрение обновлений, пока не устранят баги и не завершат дополнительное тестирование.\n\n"
            
            "🔵 Thread [thread_id] \n"
            "  • Обсуждали интеграцию нового API для синхронизации с бухгалтерскими программами. Это сократит время на ручной ввод данных на 50%.\n"
            "  • Сергей предложил добавить кэширование для ускорения работы и повышения надежности системы.\n\n"
            
            "🔵 Thread [thread_id] \n"
            "  • Мария представила план маркетинговой кампании для нового ПО по управлению складом. План включает опросы пользователей, чтобы выявить нужные функции.\n"
            "  • Цель — привлечь 500 новых B2B клиентов через LinkedIn и вебинары за три месяца.\n\n"
            
            "🔵 Thread [thread_id] \n"
            "  • Александр предложил скрипт для отдела продаж, чтобы увеличить средний чек через upsell и cross-sell. Он включил конкретные предложения услуг и лицензий.\n"
            "  • Скрипт повысил средний чек на 15%, а конверсия закрытых сделок выросла на 8%.\n\n"
            
            "🔵 Thread [thread_id] \n"
            "  • Вячеслав проанализировал конкурентов, которые тратят на 25% больше на рекламу через Google Ads, чем наша компания.\n"
            "  • Команда решила увеличить бюджет на таргетинг и пересмотреть ключевые слова, чтобы улучшить результаты.\n\n"
            
            "🔵 Thread [thread_id] \n"
            "  • Обсуждали корпоративное мероприятие с тимбилдингом. Темы включали командную работу и решение конфликтов.\n"
            "  • Решили провести его на природе с командными играми и конкурсами на решение бизнес-задач.\n\n"
            
            "🔵 Thread [thread_id] \n"
            "  • Планировали поход на выходные с подъемом на 1500 метров. Участникам потребуются трекинговые палки и специальная обувь.\n"
            "  • Согласовали снаряжение и разделили участников на группы по уровню подготовки для безопасности.\n\n"
            
            "🔵 Thread [thread_id] \n"
            "  • Аня предложила провести мастер-класс по итальянской кухне. Участники будут готовить ризотто и пасту с морепродуктами.\n"
            "  • Предложили сделать мероприятие благотворительным и передать часть средств в фонд помощи детям.\n\n"
            
            "🔵 Thread [thread_id] \n"
            "  • Обсуждали повышение квалификации в области data science, так как новые проекты требуют работы с большими данными.\n"
            "  • Решили пригласить эксперта по TensorFlow для обучения сотрудников работе с нейросетями.\n\n"
            
            "🔵 Thread [thread_id] \n"
            "  • Ольга рассказала о своем опыте на курсах по управлению проектами. Она изучила Agile и Kanban-доски.\n"
            "  • Команда рассмотрела возможность внедрения гибридной модели Scrum и Kanban для повышения эффективности.\n\n"
            
            "🔵 Thread [thread_id] \n"
            "  • Илья предложил обсудить книгу 'Lean Startup' Эрика Риса, которая помогает компаниям адаптироваться к изменениям на рынке.\n"
            "  • Договорились встретиться для обсуждения ключевых идей и применения Lean в разработке ПО.\n\n"
            
            "🔵 Thread [thread_id] \n"
            "  • Группа обсуждала покупку коммерческой недвижимости. Цены выросли на 12% за последний год, что делает покупку выгодной.\n"
            "  • Решили проанализировать возможные объекты для инвестиций, учитывая текущие ставки по ипотеке.\n\n"
            
            "🔵 Thread [thread_id] \n"
            "  • Алексей поделился планом подготовки к марафону, включая интервальные тренировки и длинные дистанции.\n"
            "  • Участники обменялись советами по восстановлению и использованию добавок для улучшения результатов.\n\n"
            
            "🔵 Thread [thread_id] \n"
            "  • Обсуждали летние отпуска и бюджетные маршруты по Европе. Елена рассказала о поездке по Греции с посещением Афин, Санторини и Крита.\n"
            "  • Участники обменялись советами по поиску дешевых билетов и аренде жилья через Airbnb.\n\n"
            
            "🔵 Thread [thread_id] \n"
            "  • Обсуждали открытие нового ресторана с японской кухней. Блюда включали суши с трюфелями и роллы с лососем и манго.\n"
            "  • Ресторан получил высокие оценки за качество и обслуживание, и предложили его как место для корпоративных мероприятий.\n\n"
            
            "🔵 Thread [thread_id] \n"
            "  • Иван рассказал о запуске стартапа, который занимается автоматизацией логистики через SaaS-решения. Привлек 500 000 долларов инвестиций.\n"
            "  • Обсудили стратегию продвижения через контент-маркетинг и рекламные кампании на бизнес-форумах.\n\n"
            f"Conversations:\n\n{message_block}"
        )
        
        logging.info(f"Generated prompt for Gemini API: {prompt}")

        # Call the Gemini API and get the summary
        summary = get_gemini_summary(prompt)
        logging.info(f"Received summary from Gemini API: {summary}")

        # Send the summary back to the user
        await update.message.reply_text(f"Key discussions:\n\n{summary}")
        
        return ConversationHandler.END
    except ValueError:
        # Log the ValueError to help debug the issue
        logging.error(f"Invalid input for number of messages: {update.message.text}")
        # Handle invalid input (non-numeric values)
        await update.message.reply_text("Please enter a valid number.")
        return ASK_MESSAGE_COUNT
    except Exception as e:
        # Log any other errors that might occur
        logging.error(f"An error occurred: {str(e)}")
        await update.message.reply_text("An error occurred while processing your request. Please try again.")
        return ConversationHandler.END

# Format the last N messages into plain text, grouped by thread_id
def format_messages(messages):
    formatted_messages = []
    
    try:
        # Group messages by thread_id
        grouped_messages = {}
        for thread_id, username, date, message_content in messages:
            if thread_id not in grouped_messages:
                grouped_messages[thread_id] = []
            grouped_messages[thread_id].append((username, date, message_content))
        
        # Format messages for each thread using thread_name
        for thread_id, msgs in grouped_messages.items():
            thread_name = get_thread_name(thread_id)  # Using thread_name instead of thread_id
            formatted_messages.append(f"🔵 {thread_name}")
            for username, date, message_content in msgs:
                logging.info(f"Formatting message: {username}, {date}, {message_content}")
                formatted_messages.append(f"  - [{date}] {username}: {message_content}")
            formatted_messages.append("")  # Add a blank line between threads
    except Exception as e:
        logging.error(f"Error formatting messages: {str(e)}")
        raise e  # Rethrow the exception after logging it
    
    return "\n".join(formatted_messages)

# Function to handle all messages and store them in the database
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        # Capture message details
        message_id = update.message.message_id
        message_text = update.message.text
        date = update.message.date.isoformat()
        user = update.effective_user
        username = user.username if user.username else user.first_name
        thread_id = update.message.message_thread_id if update.message.is_topic_message else None

        # Optionally log the thread_name
        thread_name = get_thread_name(thread_id)
        logging.info(f"Thread Name: {thread_name}")

        # Insert the message into the SQLite database
        insert_message(message_id, date, username, message_text, thread_id)

        # Log for debugging purposes
        logging.info(f"Stored message from {username} (ID: {message_id}) in the database.")

