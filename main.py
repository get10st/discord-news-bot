import os
import random
import time
import feedparser
import discord
from discord.ext import commands, tasks
from datetime import datetime
from flask import Flask
from threading import Thread

# --- 環境変数 ---
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

# --- Discord Bot準備 ---
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# --- Flask（Railway維持用）---
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is running!"
Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()

# --- 投稿済みURL追跡 ---
posted_urls = set()

# --- RSS取得（リトライ付き）---
def fetch_rss(url, retries=3, delay=5):
    for _ in range(retries):
        try:
            feed = feedparser.parse(f"{url}?nocache={random.randint(0,99999)}")
            if feed.bozo == 0 and feed.entries:
                return feed
        except Exception as e:
            print(f"⚠️ RSS取得失敗: {e}")
        time.sleep(delay)
    return None

# --- 投稿関数 ---
async def post_feed(feed_url, name, max_posts=5):
    feed = fetch_rss(feed_url)
    if not feed:
        print(f"❌ {name}: RSS取得失敗")
        return

    channel = bot.get_channel(CHANNEL_ID)
    new_count = 0
    for entry in feed.entries:
        if entry.link in posted_urls:
            continue
        msg = f"📰 [{name}] {entry.title}\n{entry.link}"
        await channel.send(msg)
        posted_urls.add(entry.link)
        new_count += 1
        await asyncio.sleep(1)
        if new_count >= max_posts:
            break

# --- スケジュール別 tasks ---
@tasks.loop(minutes=10)
async def nhk_loop():
    now = datetime.now().hour
    if 22 <= now or now < 10:
        return
    await post_feed("https://www3.nhk.or.jp/rss/news/cat0.xml", "NHK", max_posts=3)

@tasks.loop(hours=1)
async def toyokeizai_loop():
    await post_feed("https://toyokeizai.net/rss/all.xml", "東洋経済", max_posts=5)

@tasks.loop(minutes=1)
async def bbc_loop():
    now = datetime.now()
    if now.hour == 13 and now.minute % 10 == 0:
        await post_feed("http://feeds.bbci.co.uk/news/rss.xml", "BBC", max_posts=5)

@tasks.loop(minutes=1)
async def cnn_loop():
    now = datetime.now()
    if now.hour == 17 and now.minute % 10 == 0:
        await post_feed("http://rss.cnn.com/rss/edition.rss", "CNN", max_posts=5)

@tasks.loop(minutes=1)
async def reuters_loop():
    now = datetime.now()
    if now.hour == 21 and now.minute % 10 == 0:
        await post_feed("http://feeds.reuters.com/reuters/topNews", "ロイター", max_posts=5)

@tasks.loop(minutes=30)
async def arxiv_loop():
    now = datetime.now()
    if now.hour in [9, 21]:
        await post_feed("http://export.arxiv.org/rss/cs.AI", "arXiv(AI)", max_posts=3)

# --- 起動時処理 ---
@bot.event
async def on_ready():
    print(f"✅ ログイン成功: {bot.user}")
    nhk_loop.start()
    toyokeizai_loop.start()
    bbc_loop.start()
    cnn_loop.start()
    reuters_loop.start()
    arxiv_loop.start()



