import asyncio
import logging
import os

import discord
from discord.ext import commands

from fuo import cogs, config, db, log

_logger = logging.getLogger(__name__)


hostip = os.getenv("hostip") or "127.0.0.1"
proxy = f"http://{hostip}:10081"
print(f"proxy: {proxy}")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True

bot = commands.Bot(command_prefix="%", intents=intents, proxy=proxy)


@bot.event
async def on_ready():
    _logger.info(f"bot is ready!")


async def run():
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


def main():
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        pass