import discord
from discord.ext import tasks, commands
import feedparser
import os
from dotenv import load_dotenv
from datetime import datetime
import asyncio

# 環境変数読み込み
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))

# Bot定義
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)

# 重複防止用
last_links = {
    "nhk": None,
}
last_posted_dates = {
    "toyokeizai": None,
    "bbc": None,
    "cnn": None,
    "reuters": None,
    "arxiv": None
}

# チャンネル取得共通関数
def get_channel():
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print("❌ チャンネルが見つかりません")
    return channel

# 投稿タイミングの判定関数
def should_post_at(target_time: str, last_posted_key: str) -> bool:
    now = datetime.now()
    return now.strftime("%H:%M") == target_time and last_posted_dates[last_posted_key] != now.strftime("%Y-%m-%d")

# 起動時処理
@bot.event
async def on_ready():
    print(f"✅ ログイン成功: {bot.user}")
    nhk_task.start()
    toyokeizai_task.start()
    bbc_task.start()
    cnn_task.start()
    reuters_task.start()
    arxiv_task.start()

# NHK（毎時・10時〜21時限定）
@tasks.loop(minutes=60)
async def nhk_task():
    now = datetime.now()
    if now.hour < 10 or now.hour > 21:
        print("🕙 NHK: 投稿時間外")
        return

    channel = get_channel()
    if not channel:
        return

    feed = feedparser.parse("https://www3.nhk.or.jp/rss/news/cat0.xml")
    if feed.entries:
        latest = feed.entries[0]
        if latest.link != last_links["nhk"]:
            await channel.send(f"📰 **{latest.title}**\n{latest.link}")
            last_links["nhk"] = latest.link
        else:
            print("🔁 NHK: すでに投稿済み")
    else:
        await channel.send("❌ NHKニュース取得失敗")

# 各メディア共通テンプレート
async def fetch_and_post_rss(name, url, emoji, time_str):
    if not should_post_at(time_str, name):
        return
    channel = get_channel()
    if not channel:
        return

    feed = feedparser.parse(url)
    if feed.entries:
        articles = feed.entries[:5]
        message = f"{emoji} **{name.upper()} 最新記事 ({time_str})**\n\n"
        for entry in articles:
            message += f"• [{entry.title}]({entry.link})\n"
        await channel.send(message)
        last_posted_dates[name] = datetime.now().strftime("%Y-%m-%d")
    else:
        await channel.send(f"❌ {name}のニュース取得失敗")

# タスク定義（時間指定）
@tasks.loop(minutes=1)
async def toyokeizai_task():
    await fetch_and_post_rss("toyokeizai", "https://toyokeizai.net/rss/all.xml", "📢", "09:00")

@tasks.loop(minutes=1)
async def bbc_task():
    await fetch_and_post_rss("bbc", "http://feeds.bbci.co.uk/news/world/rss.xml", "🌍", "13:00")

@tasks.loop(minutes=1)
async def cnn_task():
    await fetch_and_post_rss("cnn", "http://rss.cnn.com/rss/edition.rss", "🗞", "17:00")

@tasks.loop(minutes=1)
async def reuters_task():
    await fetch_and_post_rss("reuters", "http://feeds.reuters.com/reuters/topNews", "🗞", "21:00")

@tasks.loop(minutes=1)
async def arxiv_task():
    await fetch_and_post_rss("arxiv", "http://export.arxiv.org/rss/cs.AI", "📚", "18:00")

# 起動
if __name__ == "__main__":
    bot.run(TOKEN)
