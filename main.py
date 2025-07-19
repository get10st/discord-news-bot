import discord
from discord.ext import tasks, commands
import feedparser
import os
from dotenv import load_dotenv
from datetime import datetime
import asyncio

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

# 重複防止用
last_link_nhk = None
last_posted_date_toyo = None
last_posted_date_bbc = None
last_posted_date_cnn = None
last_posted_date_reuters = None
last_posted_date_arxiv = None  # arXiv（AI）の重複防止用

@bot.event
async def on_ready():
    print(f"✅ ログイン成功: {bot.user}")
    nhk_task.start()
    toyokeizai_task.start()
    bbc_task.start()
    cnn_task.start()
    reuters_task.start()
    arxiv_task.start()  # ←これを忘れず追加！


# NHK
@tasks.loop(minutes=60)  # ← 1時間ごとに変更
async def nhk_task():
    global last_link_nhk
    now = datetime.now()
    hour = now.hour

    # 投稿時間を10〜21時に限定（10 <= hour <= 21）
    if hour < 10 or hour > 21:
        print("🕙 NHK: 投稿時間外です。スキップします。")
        return

    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print("❌ NHK: チャンネルが見つかりません")
        return

    feed = feedparser.parse("https://www3.nhk.or.jp/rss/news/cat0.xml")
    if feed.entries:
        latest = feed.entries[0]
        title = latest.title
        link = latest.link

        if link != last_link_nhk:
            await channel.send(f"📰 **{title}**\n{link}")
            last_link_nhk = link
        else:
            print("🔁 NHK: すでに投稿済みのニュースです")
    else:
        await channel.send("❌ NHKのニュースが取得できませんでした")

# 東洋経済（09:00）
@tasks.loop(minutes=1)
async def toyokeizai_task():
    global last_posted_date_toyo
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    today_str = now.strftime("%Y-%m-%d")

    if current_time == "09:00" and last_posted_date_toyo != today_str:
        channel = bot.get_channel(CHANNEL_ID)
        if not channel:
            print("❌ 東洋経済: チャンネルが見つかりません")
            return

        feed = feedparser.parse("https://toyokeizai.net/rss/all.xml")
        if feed.entries:
            articles = feed.entries[:5]
            message = "📢 **東洋経済オンライン 最新記事 (9:00)**\n\n"
            for entry in articles:
                message += f"• [{entry.title}]({entry.link})\n"
            await channel.send(message)
            last_posted_date_toyo = today_str
        else:
            await channel.send("❌ 東洋経済のニュースが取得できませんでした")

# BBC（13:00）
@tasks.loop(minutes=1)
async def bbc_task():
    global last_posted_date_bbc
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    today_str = now.strftime("%Y-%m-%d")

    if current_time == "13:00" and last_posted_date_bbc != today_str:
        channel = bot.get_channel(CHANNEL_ID)
        if not channel:
            print("❌ BBC: チャンネルが見つかりません")
            return

        feed = feedparser.parse("http://feeds.bbci.co.uk/news/world/rss.xml")
        if feed.entries:
            articles = feed.entries[:5]
            message = "🌍 **BBC World 最新記事 (13:00)**\n\n"
            for entry in articles:
                message += f"• [{entry.title}]({entry.link})\n"
            await channel.send(message)
            last_posted_date_bbc = today_str
        else:
            await channel.send("❌ BBCのニュースが取得できませんでした")

# CNN（17:00）
@tasks.loop(minutes=1)
async def cnn_task():
    global last_posted_date_cnn
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    today_str = now.strftime("%Y-%m-%d")

    if current_time == "17:00" and last_posted_date_cnn != today_str:
        channel = bot.get_channel(CHANNEL_ID)
        if not channel:
            print("❌ CNN: チャンネルが見つかりません")
            return

        feed = feedparser.parse("http://rss.cnn.com/rss/edition.rss")
        if feed.entries:
            articles = feed.entries[:5]
            message = "🗞 **CNN 最新記事 (17:00)**\n\n"
            for entry in articles:
                message += f"• [{entry.title}]({entry.link})\n"
            await channel.send(message)
            last_posted_date_cnn = today_str
        else:
            await channel.send("❌ CNNのニュースが取得できませんでした")

# ロイター（21:00）
@tasks.loop(minutes=1)
async def reuters_task():
    global last_posted_date_reuters
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    today_str = now.strftime("%Y-%m-%d")

    if current_time == "21:00" and last_posted_date_reuters != today_str:
        channel = bot.get_channel(CHANNEL_ID)
        if not channel:
            print("❌ ロイター: チャンネルが見つかりません")
            return

        feed = feedparser.parse("http://feeds.reuters.com/reuters/topNews")
        if feed.entries:
            articles = feed.entries[:5]
            message = "🗞 **ロイター 最新記事 (21:00)**\n\n"
            for entry in articles:
                message += f"• [{entry.title}]({entry.link})\n"
            await channel.send(message)
            last_posted_date_reuters = today_str
        else:
            await channel.send("❌ ロイターのニュースが取得できませんでした")
@tasks.loop(minutes=1)
async def arxiv_task():
    global last_posted_date_arxiv
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    today_str = now.strftime("%Y-%m-%d")

    if current_time == "18:00" and last_posted_date_arxiv != today_str:
        channel = bot.get_channel(CHANNEL_ID)
        if not channel:
            print("❌ arXiv: チャンネルが見つかりません")
            return

        feed = feedparser.parse("http://export.arxiv.org/rss/cs.AI")
        if feed.entries:
            articles = feed.entries[:5]
            message = "📚 **arXiv AI論文 最新記事 (18:00)**\n\n"
            for entry in articles:
                message += f"• [{entry.title}]({entry.link})\n"
            await channel.send(message)
            last_posted_date_arxiv = today_str
        else:
            await channel.send("❌ arXivから論文が取得できませんでした")


# 起動
if __name__ == "__main__":
    bot.run(TOKEN)
