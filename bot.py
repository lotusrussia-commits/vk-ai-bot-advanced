import os

from dotenv import load_dotenv
from openai import AsyncOpenAI
from vkbottle.bot import Bot, Message
from vkbottle import Keyboard, KeyboardButtonColor, Text

from memory import add_fact, get_facts, clear_memory
from history import get_history, add_message, clear_history


load_dotenv()


VK_TOKEN = os.getenv("VK_TOKEN")
PROXYAPI_TOKEN = os.getenv("PROXYAPI_TOKEN")
BASE_URL = os.getenv("PROXYAPI_BASE_URL")
MODEL = os.getenv("AI_MODEL")


bot = Bot(token=VK_TOKEN)


client = AsyncOpenAI(
    api_key=PROXYAPI_TOKEN,
    base_url=BASE_URL,
)


# Текущий режим пользователя.
# default — обычная помощь с кодом
# mentor — обучение Python
user_modes = {}


DEFAULT_PROMPT = (
    "Ты AI-помощник по программированию для начинающих. "
    "Помогай решать конкретные задачи с кодом. "
    "Отвечай понятно, простым языком и по делу. "
    "Если приводишь код, давай рабочий пример."
)


MENTOR_PROMPT = (
    "Ты — ментор по Python для начинающего программиста. "
    "Помогай пользователю изучать Python и программирование. "
    "Объясняй простыми словами и пошагово. "
    "Если пользователь показывает ошибку, сначала объясни, "
    "что она означает и почему возникла, а затем покажи способ исправления. "
    "Не перегружай ответ сложными терминами. "
    "Если можно решить задачу несколькими способами, "
    "сначала покажи самый понятный для новичка вариант. "
    "При необходимости приводи небольшие рабочие примеры кода."
)


def main_keyboard():
    """Главное меню бота."""
    return (
        Keyboard(one_time=False, inline=False)
        .add(
            Text("🐍 Учить Python"),
            color=KeyboardButtonColor.PRIMARY,
        )
        .add(
            Text("🧠 Запомнить обо мне"),
            color=KeyboardButtonColor.SECONDARY,
        )
        .row()
        .add(
            Text("💡 Помочь с кодом"),
            color=KeyboardButtonColor.POSITIVE,
        )
        .add(
            Text("ℹ️ Возможности и примеры"),
            color=KeyboardButtonColor.SECONDARY,
        )
        .row()
        .add(
            Text("🧹 Очистить память"),
            color=KeyboardButtonColor.SECONDARY,
        )
    )


def back_keyboard():
    """Клавиатура для возврата в главное меню."""
    return (
        Keyboard(one_time=False, inline=False)
        .add(
            Text("🏠 Главное меню"),
            color=KeyboardButtonColor.SECONDARY,
        )
        .add(
            Text("🧹 Очистить память"),
            color=KeyboardButtonColor.SECONDARY,
        )
    )


def build_memory_context(user_id):
    """Создаёт текст с долгосрочной памятью пользователя."""
    facts = get_facts(user_id)

    if not facts:
        return ""

    facts_text = "\n".join(
        f"- {fact}"
        for fact in facts
    )

    return (
        "\n\nДолгосрочная память о пользователе:\n"
        f"{facts_text}\n"
        "Учитывай эти сведения, когда они помогают дать более полезный ответ."
    )


def welcome_text():
    """Приветствие и главное меню."""
    return (
        "👋 Привет! Я AI-Помощник по программированию.\n\n"
        "Я могу помочь разобраться с кодом, "
        "обучать Python в режиме ментора и запоминать "
        "полезные сведения о тебе.\n\n"
        "Выбери нужный режим:\n\n"
        "🐍 Учить Python — обучение и объяснения.\n"
        "💡 Помочь с кодом — решение конкретной задачи или ошибки.\n"
        "🧠 Запомнить обо мне — сохранить информацию о себе.\n"
        "ℹ️ Возможности и примеры — подробное описание бота.\n"
        "🧹 Очистить память — удалить сохранённые сведения и историю."
    )


@bot.on.message()
async def handle_message(message: Message):
    text = message.text.strip()
    text_lower = text.lower()
    user_id = message.from_id

    # ==========================================
    # ГЛАВНОЕ МЕНЮ
    # ==========================================

    if text_lower in {
        "/start",
        "/help",
        "🏠 главное меню",
    }:
        user_modes[user_id] = "default"

        return await message.answer(
            welcome_text(),
            keyboard=main_keyboard(),
        )

    # ==========================================
    # РЕЖИМ МЕНТОРА PYTHON
    # ==========================================

    if text_lower == "🐍 учить python":
        user_modes[user_id] = "mentor"

        return await message.answer(
            "🐍 Режим «Учить Python» включён!\n\n"
            "Я буду работать как твой Python-ментор: "
            "объяснять темы простыми словами, "
            "разбирать ошибки и помогать учиться шаг за шагом.\n\n"
            "Например:\n"
            "• Что такое список в Python?\n"
            "• Объясни функции простыми словами.\n"
            "• Почему появляется эта ошибка?\n"
            "• Как работают циклы?\n\n"
            "Задавай вопрос 👇",
            keyboard=back_keyboard(),
        )

    # ==========================================
    # ЗАПОМНИТЬ О ПОЛЬЗОВАТЕЛЕ
    # ==========================================

    if text_lower == "🧠 запомнить обо мне":
        return await message.answer(
            "🧠 Запомнить обо мне\n\n"
            "Напиши, что мне стоит запомнить.\n\n"
            "Например:\n"
            "«Запомни, что я изучаю Python»\n\n"
            "Я сохраню эту информацию и смогу учитывать "
            "её в будущих ответах.",
            keyboard=back_keyboard(),
        )

    # ==========================================
    # ОБЫЧНАЯ ПОМОЩЬ С КОДОМ
    # ==========================================

    if text_lower == "💡 помочь с кодом":
        user_modes[user_id] = "default"

        return await message.answer(
            "💡 Помощь с кодом\n\n"
            "Здесь можно решить конкретную задачу по программированию: "
            "написать код, найти ошибку или разобраться с уже готовым кодом.\n\n"
            "Например:\n"
            "• Напиши функцию для сортировки списка.\n"
            "• Почему этот код выдаёт ошибку?\n"
            "• Помоги исправить мой код.\n"
            "• Объясни, что делает этот код.\n\n"
            "Отправляй задачу или код 👇",
            keyboard=back_keyboard(),
        )

    # ==========================================
    # ВОЗМОЖНОСТИ И ПРИМЕРЫ
    # ==========================================

    if text_lower == "ℹ️ возможности и примеры":
        return await message.answer(
            "ℹ️ Возможности и примеры\n\n"
            "🤖 Помощь с программированием\n"
            "Можно задать вопрос или попросить решить конкретную задачу.\n\n"
            "🐍 Ментор по Python\n"
            "Объясняет темы простыми словами и помогает разбирать ошибки.\n\n"
            "💬 История диалога\n"
            "Бот учитывает последние сообщения в текущем разговоре.\n\n"
            "🧠 Долгосрочная память\n"
            "Бот может запоминать полезные сведения о пользователе.\n\n"
            "🧹 Очистка памяти\n"
            "Можно удалить сохранённые сведения и историю диалога.\n\n"
            "💬 Примеры запросов:\n"
            "• Что такое список в Python?\n"
            "• Почему появляется эта ошибка?\n"
            "• Напиши функцию для сортировки списка.\n"
            "• Запомни, что я изучаю Python.\n\n"
            "Выбери нужный режим в главном меню.",
            keyboard=back_keyboard(),
        )

    # ==========================================
    # ОЧИСТКА ПАМЯТИ
    # ==========================================

    if text_lower == "🧹 очистить память":
        clear_memory(user_id)
        clear_history(user_id)

        return await message.answer(
            "🧹 Память очищена.\n\n"
            "Я удалил сохранённые сведения о тебе "
            "и историю текущего диалога.",
            keyboard=main_keyboard(),
        )

    # ==========================================
    # СТАРАЯ КОМАНДА /ABOUT
    # ==========================================

    if text_lower == "/about":
        return await message.answer(
            "AI-Помощник по программированию.\n\n"
            "🐍 Ментор по Python\n"
            "💡 Помощь с конкретными задачами и кодом\n"
            "💬 История текущего диалога\n"
            "🧠 Долгосрочная память пользователя\n"
            "🧹 Очистка памяти\n"
            "🎛️ Два режима работы",
            keyboard=main_keyboard(),
        )

    # ==========================================
    # /MENTOR
    # ==========================================

    if text_lower == "/mentor":
        user_modes[user_id] = "mentor"

        return await message.answer(
            "🐍 Режим «Учить Python» включён.\n\n"
            "Теперь просто отправь свой вопрос.",
            keyboard=back_keyboard(),
        )

    # ==========================================
    # /REMEMBER
    # ==========================================

    if text_lower.startswith("/remember"):
        fact = text[len("/remember"):].strip()

        if not fact:
            return await message.answer(
                "🧠 Напиши, что нужно запомнить.\n\n"
                "Например:\n"
                "/remember Я изучаю Python",
                keyboard=back_keyboard(),
            )

        add_fact(user_id, fact)

        return await message.answer(
            "🧠 Запомнил.\n\n"
            f"Сохранил: «{fact}»",
            keyboard=back_keyboard(),
        )

    # ==========================================
    # /MEMORY
    # ==========================================

    if text_lower == "/memory":
        facts = get_facts(user_id)

        if not facts:
            return await message.answer(
                "🧠 Пока я ничего о тебе не запомнил.",
                keyboard=back_keyboard(),
            )

        facts_text = "\n".join(
            f"{index}. {fact}"
            for index, fact in enumerate(facts, start=1)
        )

        return await message.answer(
            "🧠 Что я помню о тебе:\n\n"
            f"{facts_text}",
            keyboard=back_keyboard(),
        )

    # ==========================================
    # ЕСТЕСТВЕННАЯ КОМАНДА «ЗАПОМНИ»
    # ==========================================

    if text_lower.startswith("запомни"):
        fact = text[7:].strip()

        if fact.startswith(","):
            fact = fact[1:].strip()

        if fact.lower().startswith("что "):
            fact = fact[4:].strip()

        if not fact:
            return await message.answer(
                "🧠 Напиши, что именно мне запомнить.",
                keyboard=back_keyboard(),
            )

        add_fact(user_id, fact)

        return await message.answer(
            "🧠 Запомнил.\n\n"
            f"Сохраню это о тебе: «{fact}»",
            keyboard=back_keyboard(),
        )

    # ==========================================
    # ПУСТОЕ СООБЩЕНИЕ
    # ==========================================

    if not text:
        return await message.answer(
            welcome_text(),
            keyboard=main_keyboard(),
        )

    # ==========================================
    # ОПРЕДЕЛЯЕМ РЕЖИМ
    # ==========================================

    current_mode = user_modes.get(
        user_id,
        "default",
    )

    if current_mode == "mentor":
        system_prompt = MENTOR_PROMPT
    else:
        system_prompt = DEFAULT_PROMPT

    # ==========================================
    # /MENTOR С ВОПРОСОМ
    # ==========================================

    if text_lower.startswith("/mentor "):
        system_prompt = MENTOR_PROMPT
        user_modes[user_id] = "mentor"

        text = text[8:].strip()

        if not text:
            return await message.answer(
                "🐍 Напиши вопрос по Python.",
                keyboard=back_keyboard(),
            )

    # ==========================================
    # ДОБАВЛЯЕМ ДОЛГОСРОЧНУЮ ПАМЯТЬ
    # ==========================================

    memory_context = build_memory_context(user_id)
    system_prompt += memory_context

    # ==========================================
    # СОБИРАЕМ ИСТОРИЮ ДИАЛОГА
    # ==========================================

    history = get_history(user_id)

    messages = [
        {
            "role": "system",
            "content": system_prompt,
        }
    ]

    messages.extend(history)

    messages.append(
        {
            "role": "user",
            "content": text,
        }
    )

    # ==========================================
    # ЗАПРОС К AI
    # ==========================================

    try:
        response = await client.chat.completions.create(
            model=MODEL,
            messages=messages,
        )

        answer = response.choices[0].message.content

        if not answer:
            raise ValueError("AI вернул пустой ответ.")

    except Exception as error:
        print(f"Ошибка LLM: {error}")

        return await message.answer(
            "⚠️ Сейчас не удалось получить ответ от AI.\n\n"
            "Попробуй повторить запрос через несколько секунд.",
            keyboard=back_keyboard(),
        )

    # ==========================================
    # СОХРАНЯЕМ ИСТОРИЮ ДИАЛОГА
    # ==========================================

    add_message(
        user_id,
        "user",
        text,
    )

    add_message(
        user_id,
        "assistant",
        answer,
    )

    # ==========================================
    # ОТВЕТ ПОЛЬЗОВАТЕЛЮ
    # ==========================================

    return await message.answer(
        answer,
        keyboard=back_keyboard(),
    )


if __name__ == "__main__":
    bot.run()