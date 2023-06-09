import asyncio
import logging

import discord
from discord.ext import commands

from fuo import cogs, config, db, log

_logger = logging.getLogger(__name__)


intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True

bot = commands.Bot(command_prefix="%", intents=intents)


@bot.event
async def on_ready():
    _logger.info(f"bot is ready!")


async def _run():
    log.init()
    await db.init()
    try:
        async with bot:
            await bot.add_cog(cogs.RoleCog(bot))
            await bot.add_cog(cogs.ScoreCog(bot))
            await bot.add_cog(cogs.ChannelCog(bot))
            await bot.add_cog(cogs.PostCog(bot))
            await bot.add_cog(cogs.QuestionCog(bot))
            await bot.add_cog(cogs.ChatCog(bot))

            await bot.start(config.discord_token)
    finally:
        await db.close()


def run_bot():
    try:
        asyncio.run(_run())
    except KeyboardInterrupt:
        pass
