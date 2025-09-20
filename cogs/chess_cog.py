import discord
from discord import app_commands
from discord.ext import commands
import chess, chess.svg, chess.pgn
import cairosvg
import io
from PIL import Image
import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class ChessCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    logger.debug('ChessCog initialized')

    @app_commands.command(name="fen2img", description="FENを画像に変換します")
    @app_commands.describe(fen='FEN文字列 (例: rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1)')
    async def fen2img(self, interaction: discord.Interaction, fen: str):
    # Minimal logging: only invalid inputs below
        try:
            board = chess.Board(fen=fen)
        except ValueError as e:
            logger.warning(f"Invalid FEN: {e}")
            await interaction.response.send_message(f"Error: {e}", ephemeral=True)
            return

        svg_data = chess.svg.board(
            board,
            orientation=board.turn,
            size=400
        )

        png_data = cairosvg.svg2png(bytestring=svg_data.encode('utf-8'))
        with io.BytesIO(png_data) as image_binary:
            image_binary.seek(0)
            filename = f"fen_{int(time.time())}.png"
            await interaction.response.send_message(file=discord.File(fp=image_binary, filename=filename))
    # Completed successfully (no log to reduce noise)

    @app_commands.command(name="fen2img_with_details", description="FENと詳細設定から画像生成")
    @app_commands.describe(fen='FEN文字列', options='オプション: fill=マス, arrows=経路, size=数値 例: fill=e4,c5 arrows=e2-e4,c7-c5 size=600')
    async def fen2img_with_details(self, interaction: discord.Interaction, fen: str, options: str = ""):
    # Minimal logging
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
            fill_dict = { chess.parse_square(sq): '#cc0000cc' for sq in options_dict.get('fill', '').split(',') if sq } if 'fill' in options_dict else {}
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
                size=int(options_dict.get('size', 400))
            )
        except ValueError as e:
            logger.warning(f"Invalid options or FEN: {e}")
            await interaction.response.send_message(f"Error: {e}", ephemeral=True)
            return

        png_data = cairosvg.svg2png(bytestring=svg_data.encode('utf-8'))
        with io.BytesIO(png_data) as image_binary:
            image_binary.seek(0)
            filename = f"fen_{int(time.time())}.png"
            await interaction.response.send_message(file=discord.File(fp=image_binary, filename=filename))
    # Done

    @app_commands.command(name="pgn2gif", description="PGNからGIF生成")
    @app_commands.describe(pgn_str='PGN文字列 (貼り付け)')
    async def pgn2gif(self, interaction: discord.Interaction, pgn_str: str):
        # Minimal logging; long processing so defer
        if not interaction.response.is_done():
            try:
                await interaction.response.defer(thinking=True, ephemeral=True)
            except Exception:
                pass
        # サイズ制限
        if len(pgn_str) > 50_000:
            await self._safe_followup(interaction, "PGNが長すぎます (50KB超)。短くしてください。")
            return
        pgn_io = io.StringIO(pgn_str)
        game = chess.pgn.read_game(pgn_io)
        if game is None:
            logger.warning("PGN parse failed")
            await self._safe_followup(interaction, "PGNの解析に失敗しました。正しいPGNを入力してください。")
            return
        board = game.board()
        pov = chess.WHITE if game.headers.get("Result", "*") != "0-1" else chess.BLACK
        moves = list(game.mainline_moves())
        if len(moves) == 0:
            await self._safe_followup(interaction, "指し手がありません。")
            return
        if len(moves) > 400:
            await self._safe_followup(interaction, f"手数が多すぎます ({len(moves)}手)。最大400手まで対応。")
            return
        images = []
        try:
            for move in moves:
                board.push(move)
                arrows = [(move.from_square, move.to_square)]
                svg_data = chess.svg.board(
                    board,
                    orientation=pov,
                    arrows=arrows,
                    size=400
                )
                png_data = cairosvg.svg2png(bytestring=svg_data.encode('utf-8'))
                image = Image.open(io.BytesIO(png_data))
                images.append(image)
        except Exception as e:
            logger.exception("Rendering failed")
            await self._safe_followup(interaction, f"生成中にエラー: {e}")
            return

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
            filename = f"pgn_{int(time.time())}.gif"
            await self._safe_followup(interaction, file=discord.File(fp=gif_io, filename=filename))
    # Done

    async def _safe_followup(self, interaction: discord.Interaction, content: Optional[str] = None, **kwargs):
        """Send followup or initial response safely after possible defer."""
        try:
            if interaction.response.is_done():
                await interaction.followup.send(content=content, **kwargs)
            else:
                await interaction.response.send_message(content=content, **kwargs)
        except discord.NotFound:
            # Interaction expired; silently ignore
            logger.warning('Interaction expired before response could be sent.')
        except Exception:
            logger.exception('Failed to send interaction response.')

async def setup(bot):
    await bot.add_cog(ChessCog(bot))