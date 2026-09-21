import os

from dotenv import load_dotenv
from openai import AsyncOpenAI
from vkbottle.bot import Bot, Message

from memory import add_fact, get_facts


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


DEFAULT_PROMPT = (
    "Ты AI-помощник по программированию для начинающих. "
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


def build_memory_context(user_id):
    """Создаёт текст с фактами пользователя для передачи AI."""
    facts = get_facts(user_id)

    if not facts:
        return ""

    facts_text = "\n".join(f"- {fact}" for fact in facts)

    return (
        "\n\nДолгосрочная память о пользователе:\n"
        f"{facts_text}\n"
        "Учитывай эти сведения, когда они помогают дать более полезный ответ."
    )


@bot.on.message()
async def handle_message(message: Message):
    text = message.text.strip()
    user_id = message.from_id

    if text.lower() == "/help":
        return (
            "Я AI-помощник по программированию.\n\n"
            "Команды:\n"
            "/mentor — режим ментора по Python\n"
            "/remember <факт> — сохранить факт о себе\n"
            "/memory — показать сохранённые факты\n"
            "/about — информация о боте\n"
            "/help — помощь\n\n"
            "Также просто напиши свой вопрос."
        )

    if text.lower() == "/about":
        return (
            "AI-Помощник по программированию.\n"
            "Отвечаю на вопросы по Python, API, базам данных и другим темам.\n\n"
            "Дополнительные возможности:\n"
            "🐍 Ментор по Python\n"
            "🧠 Долгосрочная память пользователя"
        )

    if text.lower() == "/mentor":
        return (
            "🐍 Режим «Ментор по Python» доступен.\n\n"
            "Чтобы задать вопрос в этом режиме, используй:\n"
            "/mentor твой вопрос\n\n"
            "Например:\n"
            "/mentor Объясни, что такое список в Python"
        )

    if text.lower().startswith("/remember"):
        fact = text[len("/remember"):].strip()

        if not fact:
            return (
                "🧠 Напиши, что нужно запомнить.\n\n"
                "Например:\n"
                "/remember Я изучаю Python"
            )

        add_fact(user_id, fact)

        return (
            "🧠 Запомнил.\n\n"
            f"Сохранил: «{fact}»"
        )

    if text.lower() == "/memory":
        facts = get_facts(user_id)

        if not facts:
            return "🧠 Пока я ничего о тебе не запомнил."

        facts_text = "\n".join(
            f"{index}. {fact}"
            for index, fact in enumerate(facts, start=1)
        )

        return (
            "🧠 Что я помню о тебе:\n\n"
            f"{facts_text}"
        )

    if not text:
        return "Напиши вопрос, и я постараюсь помочь."

    system_prompt = DEFAULT_PROMPT

    if text.lower().startswith("/mentor "):
        system_prompt = MENTOR_PROMPT
        text = text[8:].strip()

        if not text:
            return (
                "🐍 Режим «Ментор по Python».\n\n"
                "Например:\n"
                "/mentor Объясни, что такое список в Python"
            )

    memory_context = build_memory_context(user_id)

    system_prompt += memory_context

    response = await client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": text,
            },
        ],
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    bot.run()