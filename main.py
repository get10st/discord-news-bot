import discord
import feedparser
import requests
from bs4 import BeautifulSoup
import asyncio
import os
from datetime import datetime
from discord.ext import commands, tasks
from flask import Flask
from threading import Thread

# ==== 環境変数 ====
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))

# ==== Flaskアプリ（Railway用）====
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running."

def run_flask():
    app.run(host='0.0.0.0', port=8080)

Thread(target=run_flask).start()

# ==== Discord Bot設定 ====
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# ==== ニュース取得関数 ====

async def post_news(title, url, prefix, channel):
    await channel.send(f"{prefix} {title}\n{url}")

def fetch_rss(url):
    try:
        feed = feedparser.parse(url)
        if feed.entries:
            return feed.entries[0].title, feed.entries[0].link
        else:
            return None
    except Exception as e:
        return None

def fetch_arxiv():
    url = "http://export.arxiv.org/rss/cs.AI"
    return fetch_rss(url)

def fetch_reuters():
    url = "http://feeds.reuters.com/reuters/topNews"
    return fetch_rss(url)

def fetch_bbc():
    url = "http://feeds.bbci.co.uk/news/world/rss.xml"
    return fetch_rss(url)

def fetch_cnn():
    url = "http://rss.cnn.com/rss/edition.rss"
    return fetch_rss(url)

def fetch_nhk():
    try:
        nhk_url = "https://www3.nhk.or.jp/news/"
        res = requests.get(nhk_url, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        headline = soup.select_one("div.content--list-main a")
        if headline:
            title = headline.text.strip()
            link = "https://www3.nhk.or.jp" + headline.get("href")
            return title, link
    except Exception:
        return None

def fetch_toyokeizai():
    try:
        url = "https://toyokeizai.net/list/feed/rss"
        return fetch_rss(url)
    except Exception:
        return None

# ==== タスクループ ====
@tasks.loop(minutes=60)
async def fetch_and_post_news():
    await bot.wait_until_ready()
    now = datetime.now().strftime("%H:%M")
    channel = bot.get_channel(CHANNEL_ID)

    sources = [
        ("🧠 arxiv", fetch_arxiv),
        ("📰 reuters", fetch_reuters),
        ("🌍 BBC", fetch_bbc),
        ("🗞 CNN", fetch_cnn),
        ("📺 NHK", fetch_nhk),
        ("📊 toyokeizai", fetch_toyokeizai),
    ]

    for label, fetcher in sources:
        try:
            news = fetcher()
            if news:
                await post_news(f"{label} 最新記事（{now}）", news[1], f"• {news[0]}", channel)
            else:
                await channel.send(f"❌ {label}のニュース取得失敗")
        except Exception as e:
            await channel.send(f"❌ {label}の取得中にエラーが発生しました: {str(e)}")

# ==== 起動イベント ====
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    fetch_and_post_news.start()

# ==== 実行 ====
if TOKEN and CHANNEL_ID:
    bot.run(TOKEN)
else:
    print("環境変数 DISCORD_BOT_TOKEN または DISCORD_CHANNEL_ID が設定されていません")




