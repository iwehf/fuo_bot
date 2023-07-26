from enum import Enum

import discord
from fastapi import HTTPException, Path
from typing_extensions import Annotated

from fuo.bot import bot


async def get_user(
    user_id: Annotated[
        int, Path(title="The discord user id", description="The discord user id")
    ]
) -> discord.User:
    user = bot.get_user(user_id)
    if user is None:
        try:
            user = await bot.fetch_user(user_id)
        except discord.errors.NotFound:
            raise HTTPException(status_code=422, detail="User not found")
    return user


async def get_guild(guild_id: int) -> discord.Guild:
    guild = bot.get_guild(guild_id)
    if guild is None:
        guild = await bot.fetch_guild(guild_id)
    return guild


async def get_channel(channel_id: int) -> discord.TextChannel:
    channel = bot.get_channel(channel_id)
    if channel is None:
        channel = await bot.fetch_channel(channel_id)
    assert isinstance(channel, discord.TextChannel)
    return channel


class OrderParam(str, Enum):
    ASC = "asc"
    DESC = "desc"
