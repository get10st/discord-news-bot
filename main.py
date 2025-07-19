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

@bot.event
async def on_ready():
    print(f"✅ ログイン成功: {bot.user}")
    nhk_task.start()
    toyokeizai_task.start()

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
