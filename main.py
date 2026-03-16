import os
import requests
import json

BOT_TOKEN = os.environ.get("BOT_TOKEN")

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=data)

def handler(event, context):
    body = json.loads(event["body"])

    if "message" in body:
        chat_id = body["message"]["chat"]["id"]
        text = body["message"].get("text", "")

        if text == "/start":
            send_message(chat_id, "Бот работает. Планировщик запущен.")

    return {
        "statusCode": 200,
        "body": "ok"
    }
