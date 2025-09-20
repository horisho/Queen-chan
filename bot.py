import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord import app_commands


load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
if not TOKEN:
    logging.error("DISCORD_BOT_TOKEN is not set.")
    exit(1)


intents = discord.Intents.default()
intents.message_content = True


handler = RotatingFileHandler('bot.log', maxBytes=5000000, backupCount=5)
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    handlers=[handler, logging.StreamHandler(sys.stdout)],
    format='%(asctime)s %(levelname)s %(message)s'
)

# discordライブラリア内部ログはWARNING以上に抑制（必要なら DISCORD_LOG_LEVEL 環境変数で変更）
discord_log_level = os.getenv('DISCORD_LOG_LEVEL', 'WARNING').upper()
logging.getLogger('discord').setLevel(getattr(logging, discord_log_level, logging.WARNING))

DEBUG_APP_CMDS = os.getenv('DEBUG_APP_CMDS') == '1'  # (今後未使用; 後方互換のため残すが参照しない)


bot = commands.Bot(command_prefix='!', intents=intents)
bot.synced_once = False  # 初回同期制御フラグ

# 即時反映を強制したい単一ギルド（環境変数で指定）
FORCE_GUILD_ID = os.getenv('FORCE_GUILD_ID')
if FORCE_GUILD_ID and not FORCE_GUILD_ID.isdigit():
    logging.warning('[CONFIG] FORCE_GUILD_ID が数値ではありません。ギルドIDではなくトークンを誤って設定している可能性があります。値先頭=%r', FORCE_GUILD_ID[:12])
force_guild_obj = discord.Object(id=int(FORCE_GUILD_ID)) if FORCE_GUILD_ID and FORCE_GUILD_ID.isdigit() else None


@bot.event
async def on_ready():
    logging.info(f'[READY] Logged in as {bot.user} (id={bot.user.id})')
    if not bot.synced_once:
        try:
            # まずグローバル同期
            synced_global = await bot.tree.sync()
            logging.info(f'[SYNC] Global commands synced count={len(synced_global)} names={[c.name for c in synced_global]}')

            # 強制ギルド同期（即時反映）
            if force_guild_obj:
                synced_guild = await bot.tree.sync(guild=force_guild_obj)
                logging.info(f'[GUILD-SYNC] count={len(synced_guild)} guild={force_guild_obj.id} names={[c.name for c in synced_guild]}')

            bot.synced_once = True
        except Exception as e:
            logging.exception(f'[ERROR][SYNC] {e}')
    else:
        logging.info('[SYNC] Already synced; skipping re-sync.')

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    await bot.process_commands(message)



@bot.event
async def on_error(event, *args, **kwargs):
    logging.exception(f"[ERROR][EVENT] {event}: {args} {kwargs}")

@bot.event
async def on_command_error(ctx, error):
    logging.error(f"[ERROR][PREFIX-CMD] {error}")

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    logging.error(f"[ERROR][APP-CMD] {interaction.command.name if interaction.command else 'unknown'}: {error}")
    if not interaction.response.is_done():
        try:
            await interaction.response.send_message(f"エラー: {error}", ephemeral=True)
        except Exception:
            pass

@app_commands.command(name='sync', description='(管理) グローバルコマンド再同期')
async def sync_command(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message('権限がありません。', ephemeral=True)
        return
    try:
        global_synced = await interaction.client.tree.sync()
        await interaction.response.send_message(
            f"Synced global commands: {len(global_synced)}", ephemeral=True
        )
    except Exception as e:
        logging.exception('Manual sync failed')
        if not interaction.response.is_done():
            await interaction.response.send_message(f"同期失敗: {e}", ephemeral=True)

bot.tree.add_command(sync_command)


# ---------------- Debug / utility slash commands ----------------
@app_commands.command(name='ping', description='疎通確認: Pongとレイテンシ(ms)を返します')
async def ping_command(interaction: discord.Interaction):
    latency_ms = round(interaction.client.latency * 1000, 1)
    await interaction.response.send_message(f'Pong! latency={latency_ms}ms', ephemeral=True)
    # PING ログは冗長のため削除

bot.tree.add_command(ping_command)


## on_interaction ログは冗長のため削除（必要なら復活可）


## debug_commands 削除（不要）


async def main():
    logging.info('Starting bot...')
    try:
        await bot.load_extension('cogs.chess_cog')
        logging.info('Loaded extension: cogs.chess_cog')
    except Exception:
        logging.exception('Failed to load extension cogs.chess_cog')
        return
    await bot.start(TOKEN)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())