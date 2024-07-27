import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

# .envから環境変数を読み込む
load_dotenv()

# インテントの設定
intents = discord.Intents.default()
intents.typing = False  # typingに関するイベントを無効化（オプション）
intents.message_content = True  # # message_contentに関するイベントを有効化（これは必須）

# Botの設定
bot = commands.Bot(command_prefix='/', intents=intents)  # インテントを指定してBotを作成

# 起動時のイベント
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} ')
    # カテゴリを読み込み
    try:
        await bot.load_extension('cogs.chess_cog')
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

# Botのトークン
try:
    TOKEN = os.environ['DISCORD_BOT_TOKEN']
    if TOKEN is None:
        raise ValueError("Token does not exist.")
except ValueError as e:
    print(f"Error: {e}")
    exit(1)

# Botを実行
bot.run(TOKEN)