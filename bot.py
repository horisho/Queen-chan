import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio

# .envから環境変数を読み込む
load_dotenv()

# インテントの設定
intents = discord.Intents.default()
intents.typing = False  # typingに関するイベントを無効化（オプション）
intents.message_content = True  # # message_contentに関するイベントを有効化（これは必須）

# Botの設定
bot = commands.Bot(command_prefix='/', intents=intents)  # インテントを指定してBotを作成

# 再接続を試みるカスタムランナー
async def run_bot():
    while True:
        try:
            await bot.start(TOKEN)
        except (discord.ConnectionClosed, asyncio.CancelledError):
            print("Connection lost, attempting to reconnect...")
            await asyncio.sleep(5)  # 5秒待機してから再接続を試みる
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            break

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
loop = asyncio.get_event_loop()
loop.run_until_complete(run_bot())