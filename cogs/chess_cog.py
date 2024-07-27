import discord
from discord.ext import commands
import chess, chess.svg
import cairosvg
import io

class ChessCog(commands.Cog, name="Chess commands"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Chess Cog on ready!')

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
            "/fen2img_with_details <FEN> [fill=e4,c5] [arrows=e2-e4,c7-c5] [size=400]"
        )
    )
    async def fen2img_with_details(self, ctx, fen: str, *, options: str = None):
        try:
            board = chess.Board(fen=fen)
            options_dict = {}
            orientation = chess.WHITE
            if options:
                orientation = chess.BLACK if options[0].startswith('b') else chess.WHITE
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
                orientation=orientation,
                fill=fill_dict,
                arrows=arrows_list,
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
    await bot.add_cog(ChessCog(bot))