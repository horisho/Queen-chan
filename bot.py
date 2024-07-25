import discord, os
from discord.ext import commands
from dotenv import load_dotenv

# .envから環境変数を読み込む
load_dotenv()

# インテントの設定
intents = discord.Intents.default()
intents.typing = False # typingに関するイベントを無効化（オプション）
intents.message_content = True # # message_contentに関するイベントを無効化（これは必須）

# Botの設定
bot = commands.Bot(command_prefix='/', intents=intents)  # インテントを指定してBotを作成

# 起動時のイベント
@bot.event
async def on_ready():
    print(f'{bot.user} がログインしました')

# "/upper"コマンドの実装
@bot.command()
async def upper(ctx, *, text):
    print("command catched!")
    upper_text = text.upper()  # テキストを大文字に変換
    await ctx.send(upper_text)  # 大文字に変換したテキストを送信

# Botのトークン
try:
    TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    if TOKEN is None:
        raise ValueError("環境変数にBOTのトークンが入ってないよ")
except ValueError as e:
    print(f"Error: {e}")
    exit(1)

# Botを実行
bot.run(TOKEN)