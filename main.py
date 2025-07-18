import discord
from discord.ext import tasks
import os
import requests
from bs4 import BeautifulSoup
import datetime
import feedparser
from keep_alive import keep_alive

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

intents = discord.Intents.default()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'ログイン成功: {client.user}')
    if not news_task.is_running():
        news_task.start()

@tasks.loop(minutes=1)
async def news_task():
    now = datetime.datetime.now()
    if now.minute == 0:
        channel = client.get_channel(CHANNEL_ID)
        if not channel:
            print("チャンネルが見つかりません")
            return

        # AI論文（9時・21時）
        if now.hour in [9, 21]:
            papers = get_papers_arxiv("https://export.arxiv.org/rss/cs.AI")
            for title, link in papers:
                embed = discord.Embed(
                    title=title,
                    url=link,
                    description="AI論文（arXiv）より",
                    color=0x9b59b6
                )
                await channel.send(embed=embed)

        # ニュース（9:日経、13:BBC、17:CNN、21:ロイター）
        if now.hour == 9:
            news = get_news_nikkei()
        elif now.hour == 13:
            news = get_news_bbc()
        elif now.hour == 17:
            news = get_news_cnn()
        elif now.hour == 21:
            news = get_news_reuters()
        else:
            return

        for title, link in news:
            embed = discord.Embed(
                title=title,
                url=link,
                description="最新ニュース",
                color=0x1abc9c
            )
            await channel.send(embed=embed)

# ニュース取得系関数
def get_news_nikkei():
    url = 'https://www.nikkei.com/'
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    articles = soup.select('a[href^="/article/"]')
    return [(a.get_text().strip(), 'https://www.nikkei.com' + a['href']) for a in articles[:5]]

def get_news_bbc():
    url = 'https://www.bbc.com/news'
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    articles = soup.select('a.gs-c-promo-heading')
    return [(a.get_text().strip(), 'https://www.bbc.com' + a['href']) for a in articles[:5]]

def get_news_cnn():
    url = 'https://edition.cnn.com/'
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    articles = soup.select('h3.cd__headline a')
    return [(a.get_text().strip(), 'https://edition.cnn.com' + a['href']) for a in articles[:5]]

def get_news_reuters():
    url = 'https://jp.reuters.com/'
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    articles = soup.select('a[data-testid="Heading"]')
    return [(a.get_text().strip(), 'https://jp.reuters.com' + a['href']) for a in articles[:5]]

def get_papers_arxiv(rss_url):
    feed = feedparser.parse(rss_url)
    return [(entry.title, entry.link) for entry in feed.entries[:3]]

# 起動
keep_alive()
client.run(TOKEN)
