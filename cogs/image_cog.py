import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import chess, chess.svg
import cairosvg
import io

class ImageCog(commands.Cog, name="Image commands"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Image Cog on ready!')

    # "/char"コマンド
    @commands.command()
    async def char2img(self, ctx, *, text: str):
        font_path = "LightNovelPOPv2.otf"
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

    # /fen2img
    @commands.command(
        help="Convert FEN to PNG format image.",
        usage=(
            "/fen2img <FEN>"
        )
    )
    async def fen2img(self, ctx, *, fen: str):
        try:
            board = chess.Board(fen=fen)
        except ValueError as e:
            await ctx.send(f"Error: {e}")
            exit(1)

        svg_data = chess.svg.board(
            board,
            orientation=board.turn,
            size=400
        )

        png_data = cairosvg.svg2png(bytestring=svg_data.encode('utf-8'))
        with io.BytesIO(png_data) as image_binary:
            image_binary.seek(0)
            await ctx.send(file=discord.File(fp=image_binary, filename='fen.png'))


    # /fen2img_with_details
    @commands.command(
        help="Convert FEN and Advanced Settings to PNG format image.",
        usage=(
            "/fen2img_with_details <FEN> [fill=\"e4,c5\"] [arrows=\"e2-e4,c7-c5\"] [size=400]"
        )
    )
    async def fen2img_with_details(self, ctx, fen: str, *, options: str = None):
        try:
            board = chess.Board(fen=fen)
            options_dict = {}
            if options:
                for option in options.split():
                    if "=" in option:
                        key, value = option.split('=', 1)
                        options_dict[key] = value
            fill_dict = { chess.parse_square(sq): '#cc0000cc' for sq in options_dict['fill'].split(',') } if 'fill' in options_dict else {}
            arrows_list = []
            if 'arrows' in options_dict:
                for item in options_dict['arrows'].split(','):
                    if "-" in item:
                        start, end = item.split('-')
                        arrows_list.append(chess.svg.Arrow(chess.parse_square(start), chess.parse_square(end)))
            svg_data = chess.svg.board(
                board,
                orientation=board.turn,
                fill=fill_dict,
                arrows=arrows_list,
                # colors=
                size=int(options_dict['size']) if 'size' in options_dict else 400
            )
        except ValueError as e:
            await ctx.send(f"Error: {e}")
            exit(1)

        png_data = cairosvg.svg2png(bytestring=svg_data.encode('utf-8'))
        with io.BytesIO(png_data) as image_binary:
            image_binary.seek(0)
            await ctx.send(file=discord.File(fp=image_binary, filename='fen.png'))

async def setup(bot):
    await bot.add_cog(ImageCog(bot))