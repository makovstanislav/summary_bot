
def build_prompt(message_block):
    prompt = (
        "Summarize the following conversations grouped by threadID (sub-chats), sort threads based on the volume of messages. "
        "Ensure the summary captures key facts, main topics, insights, or decisions made in each conversation, without excessive abstraction or redundancy. "
        "Focus on what was new, noteworthy, or decided during the discussion. Focus only on the most important threads, excluding trivial mentions. Limit the summary to no more than 1-3 bullet points per thread. "
        "Omit threads where messages lack meaningful content or reactions. If no significant interaction or follow-up occurred, omit the thread from the summary entirely. "
        "Make the summary engaging, concise, and useful, highlighting conclusions where possible. "
        "If there are no significant results or conclusions, do not force multiple bullet points—keep the summary minimal.\n"
        "The more descriptive you are about key topics covered, the better.\n"
        "Avoid redundancy or excessive length. Keep the report concise and focused on useful, noteworthy information.\n"
        "Your overall answer should be in Russian and should not exceed 2676 characters. Omit formatting.\n"
        "Don't repeat threads."
        
        "Here are some examples:\n\n"
            "🔵 Thread [thread_uid] \n"
            "  • Команда обсуждала улучшение навигации в приложении по управлению финансами. Решили объединить «Аналитику» и «Транзакции» на одном экране для удобства пользователей.\n"
            "  • A/B тестирование показало, что новая схема повысила конверсию на 20%, так что команда согласилась с идеей.\n\n"

            "🔵 Thread [thread_uid] \n"
            "  • Обсуждали редизайн сайта, чтобы ускорить загрузку страниц на мобильных устройствах. 30% пользователей жалуются на проблемы с доступом к разделу «Документы».\n"
            "  • Дизайнеры предложили упростить меню и провести тестирование с реальными пользователями, чтобы проверить новые прототипы.\n\n"

            "🔵 Thread [thread_uid] \n"
            "  • Ксения представила исследование по влиянию минималистичного дизайна на интернет-магазины: уменьшение визуальных элементов ускорило загрузку страниц на 35% и повысило конверсию на 12%.\n"
            "  • Команда согласилась применить этот подход в новом лендинге, оптимизировав графику и анимации.\n\n"

            "🔵 Thread [thread_uid] \n"
            "  • Алексей предложил перейти на AWS, чтобы сократить затраты на инфраструктуру на 40 000 долларов в год.\n"
            "  • Команда обсудила возможные риски и запустила пилотный проект для проверки совместимости баз данных.\n\n"

            "🔵 Thread [thread_uid] \n"
            "  • Анна сообщила, что время обработки заявок в новой версии CRM сократилось с 15 до 10 минут. Однако выявлены баги в аналитике продаж.\n"
            "  • Решили отложить внедрение обновлений, пока не устранят баги и не завершат дополнительное тестирование.\n\n"
        f"Conversations:\n\n{message_block}"
    )
    return prompt