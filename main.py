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

@bot.event
async def on_ready():
    print(f"✅ ログイン成功: {bot.user}")
    news_task.start()

@tasks.loop(seconds=30)  # テスト用に30秒に変更
async def news_task():

    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print("❌ チャンネルが見つかりません")
        return

    feed = feedparser.parse("https://www3.nhk.or.jp/rss/news/cat0.xml")
    if feed.entries:
        latest = feed.entries[0]
        title = latest.title
        link = latest.link
        await channel.send(f"📰 **{title}**\n{link}")
    else:
        await channel.send("❌ ニュースが取得できませんでした")

bot.run(TOKEN)

print("TOKEN:", TOKEN)
print("CHANNEL_ID:", CHANNEL_ID)



