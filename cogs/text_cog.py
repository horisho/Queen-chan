import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import io

class TextCog(commands.Cog, name="Text commands"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Text Cog on ready!')

    @commands.command()
    async def textdraw(self, ctx, *, text: str):
        font_path = "../font/KiyosunaSans-B-1.0.1.otf"
        font_size = 40
        font = ImageFont.truetype(font_path, font_size)

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

async def setup(bot):
    await bot.add_cog(TextCog(bot))