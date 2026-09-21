# История текущего диалога пользователя.
# Хранится в памяти программы и очищается после перезапуска бота.

MAX_HISTORY_MESSAGES = 10

user_histories = {}


def get_history(user_id):
    """Возвращает историю диалога пользователя."""
    return user_histories.get(str(user_id), [])


def add_message(user_id, role, content):
    """Добавляет сообщение пользователя или AI в историю."""
    user_id = str(user_id)

    if user_id not in user_histories:
        user_histories[user_id] = []

    user_histories[user_id].append(
        {
            "role": role,
            "content": content,
        }
    )

    # Оставляем только последние сообщения.
    user_histories[user_id] = user_histories[user_id][-MAX_HISTORY_MESSAGES:]


def clear_history(user_id):
    """Очищает историю диалога пользователя."""
    user_histories.pop(str(user_id), None)