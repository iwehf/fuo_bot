import logging

import discord
from discord.ext import commands

from fuo import config

_logger = logging.getLogger(__name__)


async def create_role(guild: discord.Guild):
    role = discord.utils.get(guild.roles, name=config.discord_role)
    if role is None:
        await guild.create_role(
            reason="Role for FUO bot management.",
            name=config.discord_role,
            mentionable=True,
        )
        _logger.info(f"Create role {config.discord_role} for guild {guild.name}")


class RoleCog(commands.Cog, name="role"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener(name="on_guild_available")
    async def guild_available(self, guild: discord.Guild):
        await create_role(guild=guild)

    @commands.Cog.listener(name="on_guild_join")
    async def guild_join(self, guild: discord.Guild):
        await create_role(guild=guild)
