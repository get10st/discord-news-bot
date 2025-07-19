import os
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

# .env 読み込み
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

# Intents 設定
intents = discord.Intents.default()
intents.message_content = True  # メッセージ取得（必要に応じて）

# Bot クラス
class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="/", intents=intents)
        # self.tree は self.tree ですでに存在しているので不要


    async def setup_hook(self):
        await self.tree.sync()
        print("✅ スラッシュコマンドが Discord に同期されました")

bot = MyBot()

# Bot起動時
@bot.event
async def on_ready():
    print(f"✅ ログイン成功: {bot.user}")
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send("✅ Botが起動しました！")
    else:
        print("⚠️ チャンネルが見つかりません")

# スラッシュコマンドの定義
@bot.tree.command(name="test", description="テスト用のコマンドです")
async def test_command(interaction: discord.Interaction):
    await interaction.response.send_message("✅ /test 実行成功！", ephemeral=False)

# 実行
bot.run(TOKEN)

