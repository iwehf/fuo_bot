import logging

import discord
from discord.ext import commands

from fuo import cogs, config

_logger = logging.getLogger(__name__)


intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True

bot = commands.Bot(command_prefix="%", intents=intents)

@bot.event
async def on_ready():
    _logger.info(f"bot is ready!")


async def run_bot():
    try:
        async with bot:
            await bot.add_cog(cogs.RoleCog(bot))
            await bot.add_cog(cogs.ScoreCog(bot))
            await bot.add_cog(cogs.ChannelCog(bot))
            await bot.add_cog(cogs.PostCog(bot))
            await bot.add_cog(cogs.QuestionCog(bot))
            await bot.add_cog(cogs.ChatCog(bot))

            await bot.start(config.discord_token)
    except KeyboardInterrupt:
        pass
