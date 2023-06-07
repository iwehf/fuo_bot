from discord.ext import commands
from discord import Message


async def is_command(bot: commands.Bot, message: Message) -> bool:
    ctx = await bot.get_context(message)
    return ctx.valid
