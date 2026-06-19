import os
import requests
from dotenv import load_dotenv

load_dotenv()

MAILER_KEY = os.getenv("MAILER_KEY")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
LLM_URL = os.getenv("LLM_URL")
LLM_KEY = os.getenv("LLM_KEY")
LLM_MODEL = os.getenv("LLM_MODEL")

_MAILERSEND_API = "https://api.mailersend.com/v1/email"
_FROM_EMAIL = "info@app.commit.kz"
_FROM_NAME = "Yessenov Grant Bot"


def should_send_email(question: str, answer: str) -> bool:
    """Ask the LLM whether this conversation is a serious grant inquiry."""
    try:
        response = requests.post(
            LLM_URL,
            headers={"Authorization": f"Bearer {LLM_KEY}", "Content-Type": "application/json"},
            json={
                "model": LLM_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": "You decide if a conversation is a serious grant inquiry. Reply only YES or NO."
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Question: {question}\n"
                            f"Answer: {answer}\n"
                            "Is this a serious inquiry about applying for a grant or scholarship?"
                        )
                    }
                ]
            },
            timeout=15
        )
        result = response.json()["choices"][0]["message"]["content"]
        return "YES" in result.upper()
    except Exception:
        return False


def send_email_summary(user_id: int, question: str, answer: str) -> None:
    """Send a brief inquiry summary to the admin via MailerSend."""
    try:
        response = requests.post(
            _MAILERSEND_API,
            headers={
                "Authorization": f"Bearer {MAILER_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "from": {"email": _FROM_EMAIL, "name": _FROM_NAME},
                "to": [{"email": ADMIN_EMAIL, "name": "Admin"}],
                "subject": f"Новый запрос о гранте — пользователь {user_id}",
                "html": (
                    f"<h2>Новый серьёзный запрос из чата</h2>"
                    f"<p><b>Пользователь ID:</b> {user_id}</p>"
                    f"<p><b>Вопрос:</b> {question}</p>"
                    f"<p><b>Ответ бота:</b> {answer}</p>"
                    f"<hr><p>Yessenov Foundation Grant Bot</p>"
                ),
                "text": f"Пользователь {user_id}\nВопрос: {question}\nОтвет: {answer}"
            },
            timeout=15
        )
        print(f"Email sent: {response.status_code}")
    except Exception as e:
        print(f"Email error: {e}")


def send_report(user_id: int, history: list) -> None:
    """Send the full conversation history to the admin on /sendreport."""
    try:
        history_html = "".join(
            f"<p><b>{msg['role'].upper()}:</b> {msg['content']}</p>"
            for msg in history
        )
        history_text = "\n".join(
            f"{msg['role'].upper()}: {msg['content']}"
            for msg in history
        )
        response = requests.post(
            _MAILERSEND_API,
            headers={
                "Authorization": f"Bearer {MAILER_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "from": {"email": _FROM_EMAIL, "name": _FROM_NAME},
                "to": [{"email": ADMIN_EMAIL, "name": "Admin"}],
                "subject": f"Отчёт разговора — пользователь {user_id}",
                "html": f"<h2>История разговора</h2>{history_html}",
                "text": history_text
            },
            timeout=15
        )
        print(f"Report sent: {response.status_code}")
    except Exception as e:
        print(f"Report error: {e}")
