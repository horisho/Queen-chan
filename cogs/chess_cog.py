import discord
from discord.ext import commands
import chess, chess.svg, chess.pgn
import cairosvg
import io
from PIL import Image

class ChessCog(commands.Cog, name="Chess commands"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Chess Cog on ready!')

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

    @commands.command(
        help="Convert PGN to GIF format.",
        usage=(
            "/pgn2gif <PGN>"
        )
    )
    async def pgn2gif(self, ctx, *, pgn_str: str = None):
        # メッセージの添付ファイルが存在する場合
        if ctx.message.attachments:
            file = ctx.message.attachments[0]
            if file.filename.endswith(".pgn"):
                pgn_str = await file.read()
                pgn_str = pgn_str.decode('utf-8')
            else:
                await ctx.send("Please upload a PGN file.")
                return
        elif pgn_str:
            # コマンド引数としてPGN文字列が提供された場合
            pgn_str = pgn_str
        else:
            await ctx.send("You must provide either a PGN string or upload a PGN file.")
            return

        pgn_io = io.StringIO(pgn_str)
        game = chess.pgn.read_game(pgn_io)
        board = game.board()
        pov = chess.WHITE
        if game.headers.get("Result", "*") == "0-1":
            pov = chess.BLACK
        images = []
        prev_board = board.copy()
        for move in game.mainline_moves():
            board.push(move)
            # 差分を計算
            arrows = [ (move.from_square, move.to_square) ]
            svg_data = chess.svg.board(
                board,
                orientation=pov,
                arrows=arrows,
                size=400
            )
            png_data = cairosvg.svg2png(bytestring=svg_data.encode('utf-8'))
            image = Image.open(io.BytesIO(png_data))
            images.append(image)

        with io.BytesIO() as gif_io:
            images[0].save(
                gif_io,
                format='GIF',
                save_all=True,
                append_images=images[1:],
                duration=500,
                loop=0
            )
            gif_io.seek(0)
            await ctx.send(file=discord.File(fp=gif_io, filename='pgn.gif'))

async def setup(bot):
    await bot.add_cog(ChessCog(bot))