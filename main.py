import os
import requests

BOT_TOKEN = os.environ.get("BOT_TOKEN")

def handler(event, context):
    return {
        "statusCode": 200,
        "body": "Bot is running"
    }
