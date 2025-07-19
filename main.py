import asyncio
from datetime import datetime

@client.event
async def on_ready():
    print(f"✅ ログイン成功: {client.user}")
    channel = client.get_channel(CHANNEL_ID)
    if channel:
        await channel.send("✅ Botの起動テスト成功！")
        
        # テスト用の1回送信
        await channel.send("📰 テストニュース投稿")
        
        # ここからループ処理（例：10秒おきに投稿）
        async def post_news_loop():
            while True:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                await channel.send(f"🕐 {now} ニューステスト送信中…")
                await asyncio.sleep(10)  # 10秒おきに送信（本番では3600秒 = 1時間）

        client.loop.create_task(post_news_loop())
    else:
        print("⚠️ チャンネルが見つかりません")
