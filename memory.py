import json
from pathlib import Path


MEMORY_FILE = Path("user_memory.json")


def load_memory():
    """Загружает всю память пользователей."""
    if not MEMORY_FILE.exists():
        return {}

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return {}


def save_memory(memory):
    """Сохраняет память пользователей."""
    with open(MEMORY_FILE, "w", encoding="utf-8") as file:
        json.dump(memory, file, ensure_ascii=False, indent=2)


def add_fact(user_id, fact):
    """Добавляет новый факт о пользователе."""
    memory = load_memory()

    user_id = str(user_id)

    if user_id not in memory:
        memory[user_id] = []

    if fact not in memory[user_id]:
        memory[user_id].append(fact)

    save_memory(memory)


def get_facts(user_id):
    """Возвращает сохранённые факты пользователя."""
    memory = load_memory()
    return memory.get(str(user_id), [])