import discord, os, io
from discord.ext import commands
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont
from math import ceil

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
async def upper(ctx, *, text: str):
    print("command catched!")
    upper_text = text.upper()  # テキストを大文字に変換
    await ctx.send(upper_text)  # 大文字に変換したテキストを送信

# "/char"コマンドの実装
@bot.command()
async def char(ctx, *, text: str):
    args = text.split('\n')
    font_path = "LightNovelPOPv2.otf"
    font_size = 40
    font = ImageFont.truetype(font_path, font_size)

    text_width = max(
        ImageDraw.Draw(
            Image.new('RGB', (1, 1), (255, 255, 255))
        ).textlength(arg, font=font) for arg in args
    )
    text_height = font_size

    image_width = ceil(text_width + font_size / 2)
    image_height = ceil((text_height + font_size / 2 ) * len(args))

    image = Image.new('RGB', (image_width, image_height), color='white')
    draw = ImageDraw.Draw(image)

    text_x = 10
    text_y = 0 # なぜか0で上手くいった、行間のせい？　
    draw.text((text_x, text_y), text, font=font, fill='black')

    with io.BytesIO() as image_binary:
        image.save(image_binary, 'PNG')
        image_binary.seek(0)
        await ctx.send(file=discord.File(fp=image_binary, filename='text.png'))

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