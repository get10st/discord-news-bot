import discord
from discord.ext import commands
import os  # ← 追加

intents = discord.Intents.default()
intents.message_content = True  # 特権インテントを有効に

bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ ログイン成功: {bot.user}")

@bot.command()
async def test(ctx):
    await ctx.send("✅ /test 実行成功！")

# Railway の環境変数から読み込む
TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)
