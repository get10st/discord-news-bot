import discord
from discord.ext import tasks, commands
import feedparser
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

last_link = None  # 重複投稿防止用のグローバル変数

@bot.event
async def on_ready():
    print(f"✅ ログイン成功: {bot.user}")
    news_task.start()

@tasks.loop(minutes=15)  # テスト用：30秒ごとに実行
async def news_task():
    global last_link
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print("❌ チャンネルが見つかりません")
        return

    feed = feedparser.parse("https://www3.nhk.or.jp/rss/news/cat0.xml")
    if feed.entries:
        latest = feed.entries[0]
        title = latest.title
        link = latest.link

        if link != last_link:
            await channel.send(f"📰 **{title}**\n{link}")
            last_link = link
        else:
            print("🔁 すでに投稿済みのニュースです")
    else:
        await channel.send("❌ ニュースが取得できませんでした")

bot.run(TOKEN)
