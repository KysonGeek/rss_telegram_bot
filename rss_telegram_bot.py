import os
import time
import requests
import feedparser
from dotenv import load_dotenv
from mysql_adapter import query, insert, load_keyword
from datetime import datetime
# 加载环境变量
load_dotenv()

RSS_URL = os.getenv("RSS_URL")
TELEGRAM_API = os.getenv("TELEGRAM_API")
CHAT_ID = os.getenv("CHAT_ID")
SLEEP_S = int(os.getenv("SLEEP_S"))

def load_sent():
    return load_keyword()

def load_url(url):
    return query(url)

def send_to_telegram(text):
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "MarkdownV2"
    }
    response = requests.get(TELEGRAM_API, params=payload)
    if response.status_code != 200:
        print(f"❌ Failed to send: {response.text}")
    else:
        print(f"✅ Sent: {text}")

def monitor_rss():
    while True:
        now = datetime.now()
        print("🔍 Checking RSS feed... now: %s" % now)

        feed = feedparser.parse(RSS_URL)
        keyword_DB = load_sent()
        for entry in feed.entries:
            if keyword_DB and not any(keyword in entry.title for keyword in keyword_DB):
                continue
            sent_links = query(entry.link)
            if not sent_links:
                title = entry.title
                link = entry.link
                summary = entry.summary if 'summary' in entry else ''
                escaped_title = escape_markdown(title)
                escaped_link = escape_markdown(link)
                message = f"[{escaped_title}]({escaped_link})"
                print("message %s" % message)
                send_to_telegram(message)

                insert(title, summary, link)
            else:
                print("skip")

        time.sleep(SLEEP_S)
def escape_markdown(text):
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    return ''.join(['\\' + c if c in escape_chars else c for c in text])

if __name__ == "__main__":
    monitor_rss()
