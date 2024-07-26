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
    ascent, _ = font.getmetrics()

    bbox = ImageDraw.Draw(
        Image.new('RGB', (1, 1), (255, 255, 255))
    ).multiline_textbbox((0, 0), text, font=font, spacing=4)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    padding = int(font_size * 0.2)
    image_width = text_width + padding * 2
    image_height = text_height + padding * 2

    image = Image.new('RGB', (image_width, image_height), color='white')
    draw = ImageDraw.Draw(image)

    # なぜかbboxの開始位置が(0, 0)にならないので原点を合わせておく
    text_x = padding - bbox[0]
    text_y = padding - bbox[1]
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