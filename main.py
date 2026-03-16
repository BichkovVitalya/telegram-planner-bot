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


def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=data)


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

    if "message" in data:

        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":

            ensure_user(chat_id)

            send_message(
                chat_id,
                "🏢 Панель управления\n\n📅 Календарь\n📋 Задачи\n📊 Загрузка"
            )

    return "ok"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
