import discord
from discord.ext import tasks, commands
import feedparser
import os
from dotenv import load_dotenv
from datetime import datetime
import asyncio
from flask import Flask
import threading

# 環境変数読み込み
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))

# Discord botの設定
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

# Flask アプリ（Railway永続稼働用）
app = Flask(__name__)
@app.route("/")
def home():
    return "✅ NewsBot is running!"

def run_web():
    port = int(os.environ.get("PORT", 3000))  # Railway用にPORT環境変数も考慮
    app.run(host="0.0.0.0", port=port)

# 起動時の処理
@bot.event
async def on_ready():
    print(f"✅ ログイン成功: {bot.user}")
    nhk_task.start()
    toyokeizai_task.start()
    bbc_task.start()
    cnn_task.start()
    reuters_task.start()
    arxiv_task.start()

# ===== 重複投稿防止用 =====
last_link_nhk = None
last_posted_date_toyo = None
last_posted_date_bbc = None
last_posted_date_cnn = None
last_posted_date_reuters = None
last_posted_date_arxiv = None

# ===== 各ニュースタスク =====

# NHK（1時間おき、10〜21時）
@tasks.loop(minutes=60)
async def nhk_task():
    global last_link_nhk
    now = datetime.now()
    hour = now.hour
    if hour < 10 or hour > 21:
        print("🕙 NHK: 投稿時間外です。スキップします。")
        return
    channel = bot.get_channel(CHANNEL_ID)
    feed = feedparser.parse("https://www3.nhk.or.jp/rss/news/cat0.xml")
    if feed.entries:
        entry = feed.entries[0]
        if entry.link != last_link_nhk:
            await channel.send(f"📰 **{entry.title}**\n{entry.link}")
            last_link_nhk = entry.link

# 東洋経済（09:00）
@tasks.loop(minutes=1)
async def toyokeizai_task():
    global last_posted_date_toyo
    now = datetime.now()
    if now.strftime("%H:%M") == "09:00" and last_posted_date_toyo != now.strftime("%Y-%m-%d"):
        channel = bot.get_channel(CHANNEL_ID)
        feed = feedparser.parse("https://toyokeizai.net/rss/all.xml")
        if feed.entries:
            articles = feed.entries[:5]
            msg = "📢 **東洋経済オンライン 最新記事 (9:00)**\n\n"
            msg += "\n".join(f"• [{a.title}]({a.link})" for a in articles)
            await channel.send(msg)
            last_posted_date_toyo = now.strftime("%Y-%m-%d")

# BBC（13:00）
@tasks.loop(minutes=1)
async def bbc_task():
    global last_posted_date_bbc
    now = datetime.now()
    if now.strftime("%H:%M") == "13:00" and last_posted_date_bbc != now.strftime("%Y-%m-%d"):
        channel = bot.get_channel(CHANNEL_ID)
        feed = feedparser.parse("http://feeds.bbci.co.uk/news/world/rss.xml")
        if feed.entries:
            articles = feed.entries[:5]
            msg = "🌍 **BBC World 最新記事 (13:00)**\n\n"
            msg += "\n".join(f"• [{a.title}]({a.link})" for a in articles)
            await channel.send(msg)
            last_posted_date_bbc = now.strftime("%Y-%m-%d")

# CNN（17:00）
@tasks.loop(minutes=1)
async def cnn_task():
    global last_posted_date_cnn
    now = datetime.now()
    if now.strftime("%H:%M") == "17:00" and last_posted_date_cnn != now.strftime("%Y-%m-%d"):
        channel = bot.get_channel(CHANNEL_ID)
        feed = feedparser.parse("http://rss.cnn.com/rss/edition.rss")
        if feed.entries:
            articles = feed.entries[:5]
            msg = "🗞 **CNN 最新記事 (17:00)**\n\n"
            msg += "\n".join(f"• [{a.title}]({a.link})" for a in articles)
            await channel.send(msg)
            last_posted_date_cnn = now.strftime("%Y-%m-%d")

# ロイター（21:00）
@tasks.loop(minutes=1)
async def reuters_task():
    global last_posted_date_reuters
    now = datetime.now()
    if now.strftime("%H:%M") == "21:00" and last_posted_date_reuters != now.strftime("%Y-%m-%d"):
        channel = bot.get_channel(CHANNEL_ID)
        feed = feedparser.parse("http://feeds.reuters.com/reuters/topNews")
        if feed.entries:
            articles = feed.entries[:5]
            msg = "🗞 **ロイター 最新記事 (21:00)**\n\n"
            msg += "\n".join(f"• [{a.title}]({a.link})" for a in articles)
            await channel.send(msg)
            last_posted_date_reuters = now.strftime("%Y-%m-%d")

# arXiv（AI）（18:00）
@tasks.loop(minutes=1)
async def arxiv_task():
    global last_posted_date_arxiv
    now = datetime.now()
    if now.strftime("%H:%M") == "18:00" and last_posted_date_arxiv != now.strftime("%Y-%m-%d"):
        channel = bot.get_channel(CHANNEL_ID)
        feed = feedparser.parse("http://export.arxiv.org/rss/cs.AI")
        if feed.entries:
            articles = feed.entries[:5]
            msg = "📚 **arXiv AI論文 最新記事 (18:00)**\n\n"
            msg += "\n".join(f"• [{a.title}]({a.link})" for a in articles)
            await channel.send(msg)
            last_posted_date_arxiv = now.strftime("%Y-%m-%d")

# ===== 起動 =====
if __name__ == "__main__":
    # Flaskを別スレッドで起動（Railway対策）
    threading.Thread(target=run_web).start()

    # Discord Bot起動
    bot.run(TOKEN)

