import os
import discord
from dotenv import load_dotenv

load_dotenv()

# トークンとチャンネルIDの読み込み
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

# インテント設定
intents = discord.Intents.default()
client = discord.Client(intents=intents)  # ←これをイベント定義より前に置く！

# イベント定義
@client.event
async def on_ready():
    print(f"ログイン成功: {client.user}")
    channel = client.get_channel(CHANNEL_ID)
    if channel:
        await channel.send("✅ Botの起動テスト成功！")
    else:
        print("⚠️ チャンネルが見つかりません")

# 実行
client.run(TOKEN)
