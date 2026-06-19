import os
import asyncio
import httpx
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from rag import find_relevant, load_chunks
from mailer import should_send_email, send_email_summary, send_report

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
LLM_URL = os.getenv("LLM_URL")
LLM_KEY = os.getenv("LLM_KEY")
LLM_MODEL = os.getenv("LLM_MODEL")

SYSTEM_PROMPT = """You are a precise assistant for the Shakhmardan Yessenov Foundation.

STRICT RULES - follow these exactly:
1. Answer ONLY using information from the provided context.
2. If context does not contain the answer - say EXACTLY:
   "В моих данных нет этой информации. Пожалуйста, проверьте актуальную информацию на yessenovfoundation.org"
3. NEVER invent or guess: dates, deadlines, amounts, requirements, names.
4. NEVER say a specific date or number unless it appears word-for-word in the context.
5. If asked about deadlines and context has no date - say you don't know the current deadline.
6. Reply in the same language the user writes - Russian, Kazakh, or English.
7. Be concise - maximum 5-6 sentences per answer.

If you are not 100% sure something is in the context - do not say it."""

chunks = []
user_history = {}


async def get_llm_answer(question: str, context: str) -> str:
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            LLM_URL,
            headers={"Authorization": f"Bearer {LLM_KEY}", "Content-Type": "application/json"},
            json={
                "model": LLM_MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
                ]
            }
        )
        return response.json()["choices"][0]["message"]["content"]


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Сәлем! Привет! Hello!\n\n"
        "Я помощник фонда Шахмардана Есенова 🎓\n\n"
        "Спросите меня про гранты, стипендии и программы фонда.\n"
        "Напишите /help чтобы увидеть примеры вопросов."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Примеры вопросов:\n\n"
        "• Какие гранты есть в фонде?\n"
        "• Кто может подать заявку?\n"
        "• Каковы требования к кандидатам?\n"
        "• Как подать заявку на грант?\n"
        "• Какой размер стипендии?\n"
        "• Какие программы есть для студентов?\n"
        "• What programs does the foundation offer?\n\n"
        "Напишите /sendreport чтобы отправить историю разговора."
    )


async def sendreport_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    history = user_history.get(user_id, [])
    if not history:
        await update.message.reply_text("История разговора пуста.")
        return
    send_report(user_id, history)
    await update.message.reply_text("Отчёт отправлен администратору.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    question = update.message.text

    if user_id not in user_history:
        user_history[user_id] = []
    user_history[user_id].append({"role": "user", "content": question})
    user_history[user_id] = user_history[user_id][-10:]

    await update.message.chat.send_action("typing")

    try:
        relevant = find_relevant(question, chunks, top_k=5)
        context_text = "\n\n---\n\n".join(relevant)
        answer = await get_llm_answer(question, context_text)
        user_history[user_id].append({"role": "assistant", "content": answer})
        await update.message.reply_text(answer)
        if should_send_email(question, answer):
            send_email_summary(user_id, question, answer)
    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text("Извините, произошла ошибка. Попробуйте позже.")


def main():
    global chunks
    print("Loading chunks...")
    chunks = load_chunks()
    print(f"Loaded {len(chunks)} chunks")

    asyncio.set_event_loop(asyncio.new_event_loop())
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("sendreport", sendreport_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running... Press Ctrl+C to stop")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
