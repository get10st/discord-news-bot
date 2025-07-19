import discord
from discord.ext import tasks, commands
import feedparser
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

last_link_nhk = None  # NHKの重複防止用
last_posted_date_toyo = None  # 東洋経済の重複防止用（日付）
last_posted_date_bbc = None
last_posted_date_cnn = None


@bot.event
async def on_ready():
    print(f"✅ ログイン成功: {bot.user}")
    nhk_task.start()
    toyokeizai_task.start()
    bbc_task.start()
    cnn_task.start()



@tasks.loop(minutes=15)
async def nhk_task():
    global last_link_nhk
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

            last_posted_date_bbc = None  # BBCの重複防止（日付）

@tasks.loop(minutes=1)
async def bbc_task():
    global last_posted_date_bbc
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    today_str = now.strftime("%Y-%m-%d")

    if last_posted_date_bbc != today_str:
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


import asyncio

async def main():
    async with bot:
        await bot.start(TOKEN)

asyncio.run(main())
