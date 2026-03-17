import os
import requests
from flask import Flask, request
from supabase import create_client
import uuid

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def send_message(chat_id, text, keyboard=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text,
        "reply_markup": keyboard
    }
    requests.post(url, json=data)


def edit_message(chat_id, message_id, text, keyboard=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText"
    data = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "reply_markup": keyboard
    }
    requests.post(url, json=data)


def main_menu():
    return {
        "inline_keyboard": [
            [{"text": "📅 Календарь", "callback_data": "calendar"}],
            [{"text": "📋 Задачи", "callback_data": "tasks"}],
            [{"text": "📊 Загрузка", "callback_data": "load"}],
            [{"text": "👥 Клиенты", "callback_data": "clients"}],
            [{"text": "💰 Финансы", "callback_data": "finance"}],
            [{"text": "⚙️ Настройки", "callback_data": "settings"}],
        ]
    }


def tasks_menu():
    return {
        "inline_keyboard": [
            [{"text": "➕ Добавить задачу", "callback_data": "add_task"}],
            [{"text": "📄 Мои задачи", "callback_data": "list_tasks"}],
            [{"text": "⬅ Назад", "callback_data": "back_main"}],
        ]
    }


def ensure_user(telegram_id):

    user = supabase.table("users") \
        .select("*") \
        .eq("telegram_id", telegram_id) \
        .execute()

    if user.data:
        return user.data[0]["id"]

    user_id = str(uuid.uuid4())

    supabase.table("users").insert({
        "id": user_id,
        "telegram_id": telegram_id
    }).execute()

    workspace_id = str(uuid.uuid4())

    supabase.table("workspaces").insert({
        "id": workspace_id,
        "name": f"Компания {telegram_id}",
        "type": "company",
        "created_by": user_id
    }).execute()

    supabase.table("workspace_members").insert({
        "workspace_id": workspace_id,
        "user_id": user_id,
        "role": "owner",
        "default_daily_hours": 8
    }).execute()

    return user_id


@app.route("/", methods=["POST"])
def webhook():

    data = request.json

    # Сообщение
    if "message" in data:

        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            ensure_user(chat_id)

            send_message(
                chat_id,
                "🏢 Панель управления",
                main_menu()
            )

    # Нажатие кнопки
    if "callback_query" in data:

        query = data["callback_query"]
        chat_id = query["message"]["chat"]["id"]
        message_id = query["message"]["message_id"]
        action = query["data"]

        if action == "tasks":
            edit_message(
                chat_id,
                message_id,
                "📋 Задачи",
                tasks_menu()
            )

        elif action == "back_main":
            edit_message(
                chat_id,
                message_id,
                "🏢 Панель управления",
                main_menu()
            )

    return "ok"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
