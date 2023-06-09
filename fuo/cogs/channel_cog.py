import logging

import discord
import sqlalchemy as sa
from discord.ext import commands
from typing_extensions import Annotated

from fuo import db, models, utils, config

_logger = logging.getLogger(__name__)


class ChannelCog(commands.Cog, name="channel"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        name="set-channel-type",
        help="Set a channel to the specified type. "
        "Score types can be POST, QUESTION or CHAT. "
        "In the POST channel, sending messages and making reactions can earn POST scores. "
        "In the QUESTION channel, answering questions and making reactions can earn QUESTION scores. "
        "In CHAT channels, sending messages and making reactions can earn CHAT scores. "
        "In one guild, the POST channel and the QUESTION channel are unique, and there can be several CHAT channels.",
    )
    @commands.has_role(config.discord_role)
    async def set_channel(
        self,
        ctx: commands.Context,
        channel: discord.TextChannel,
        channel_type: Annotated[models.ChannelType, utils.to_channel_type],
    ):
        assert ctx.guild is not None
        guild_id = ctx.guild.id
        channel_id = channel.id

        async with db.session_scope() as sess:
            q = (
                sa.select(models.ChannelConfig)
                .where(models.ChannelConfig.guild_id == guild_id)
                .where(models.ChannelConfig.channel_id == channel_id)
                .where(models.ChannelConfig.channel_type == channel_type)
            )
            channel_conf = (await sess.execute(q)).scalar_one_or_none()
            if (
                channel_conf is not None
                and channel_conf.channel_id != channel_id
                and channel_type in [models.ChannelType.POST, models.ChannelType.QUESTION]
            ):
                channel_conf.channel_id = channel_id
            else:
                channel_conf = models.ChannelConfig(
                    guild_id=guild_id,
                    channel_id=channel_id,
                    channel_type=channel_type,
                )
                sess.add(channel_conf)
            await sess.commit()

        _logger.info(f"set channel {channel.name} type {channel_type.name}")

    @commands.command(
        name="remove-channel-type", help="Remove the specified type of the channel."
    )
    @commands.has_role(config.discord_role)
    async def remove_channel(
        self,
        ctx: commands.Context,
        channel: discord.TextChannel,
        channel_type: Annotated[models.ChannelType, utils.to_channel_type],
    ):
        assert ctx.guild is not None
        guild_id = ctx.guild.id
        channel_id = channel.id

        async with db.session_scope() as sess:
            q = (
                sa.select(models.ChannelConfig)
                .where(models.ChannelConfig.guild_id == guild_id)
                .where(models.ChannelConfig.channel_id == channel_id)
                .where(models.ChannelConfig.channel_type == channel_type)
            )
            channel_conf = (await sess.execute(q)).scalar_one_or_none()
            if channel_conf is not None:
                await sess.delete(channel_conf)
                await sess.commit()
                _logger.info(f"remove channel {channel.name} type {channel_type.name}")

    @commands.command(name="get-channel-type", help="Get type of the specifie channel.")
    @commands.has_role(config.discord_role)
    async def get_channel_type(
        self, ctx: commands.Context, channel: discord.TextChannel
    ):
        assert ctx.guild is not None
        guild_id = ctx.guild.id
        channel_id = channel.id

        async with db.session_scope() as sess:
            q = (
                sa.select(models.ChannelConfig)
                .where(models.ChannelConfig.guild_id == guild_id)
                .where(models.ChannelConfig.channel_id == channel_id)
            )
            channel_confs = (await sess.execute(q)).scalars().all()
            if len(channel_confs) > 0:
                channel_types = [conf.channel_type.name for conf in channel_confs]
                channel_type_str = ", ".join(channel_types)
                await ctx.send(f"channel {channel.name} types: {channel_type_str}")

    async def check_channel_type(
        self, guild_id: int, channel_id: int, channel_type: models.ChannelType
    ) -> bool:
        async with db.session_scope() as sess:
            q = (
                sa.select(sa.func.count(models.ChannelConfig.id))
                .where(models.ChannelConfig.guild_id == guild_id)
                .where(models.ChannelConfig.channel_id == channel_id)
                .where(models.ChannelConfig.channel_type == channel_type)
            )

            count = (await sess.execute(q)).scalar_one()
            return count > 0

    async def cog_command_error(self, ctx: commands.Context, error: Exception):
        _logger.error(error)
