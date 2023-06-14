import logging
from typing import Any, Optional

import discord
import sqlalchemy as sa
from discord.ext import commands
from typing_extensions import Annotated

from fuo import config, db, models, utils

_logger = logging.getLogger(__name__)


class ChannelTypeNotFound(commands.CommandError):
    def __init__(self, channel_name: str):
        self.channel_name = channel_name
        super().__init__()


class ChannelTypeExists(commands.CommandError):
    def __init__(self, channel_name: str, channel_type: models.ChannelType):
        self.channel_name = channel_name
        self.channel_type = channel_type
        super().__init__()


class ChannelCog(commands.Cog, name="channel"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._unique_channel_types = [models.ChannelType.QUESTION]

    def _is_unique_channel(self, channel_type: models.ChannelType) -> bool:
        return channel_type in self._unique_channel_types

    @commands.command(
        name="set-channel-type",
        help="Set a channel to the specified type. "
        "Score types can be POST, QUESTION or CHAT. "
        "In the POST channel, sending messages and making reactions can earn POST scores. "
        "In the QUESTION channel, answering questions and making reactions can earn QUESTION scores. "
        "In CHAT channels, sending messages and making reactions can earn CHAT scores. "
        "In one guild, the QUESTION channel is unique, and there can be several POST or CHAT channels.",
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
            # one channel can only have one type
            q = (
                sa.select(models.ChannelConfig)
                .where(models.ChannelConfig.guild_id == guild_id)
                .where(models.ChannelConfig.channel_id == channel_id)
            )
            channel_conf = (await sess.execute(q)).scalar_one_or_none()
            if channel_conf is not None:
                raise ChannelTypeExists(
                    channel_name=channel.name, channel_type=channel_type
                )

            if self._is_unique_channel(channel_type):
                # for unique channel type, change the old channel type record
                q = (
                    sa.select(models.ChannelConfig)
                    .where(models.ChannelConfig.guild_id == guild_id)
                    .where(models.ChannelConfig.channel_type == channel_type)
                )
                old_channel_conf = (await sess.execute(q)).scalar_one_or_none()
                if old_channel_conf is not None:
                    old_channel_conf.channel_id = channel_id
                else:
                    channel_conf = models.ChannelConfig(
                        guild_id=guild_id,
                        channel_id=channel_id,
                        channel_type=channel_type,
                    )
                    sess.add(channel_conf)
            else:
                # for non unique channel type, add new channel type record
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
            else:
                raise ChannelTypeNotFound(channel_name=channel.name)

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
            channel_conf = (await sess.execute(q)).scalar_one_or_none()
            if channel_conf is not None:
                await ctx.send(
                    f"channel {channel.name} type: {channel_conf.channel_type.name}"
                )
            else:
                raise ChannelTypeNotFound(channel_name=channel.name)

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
        if isinstance(error, ChannelTypeNotFound):
            await ctx.send(f"Channel {error.channel_name} has no type now.")
        elif isinstance(error, ChannelTypeExists):
            await ctx.send(
                f"Channel {error.channel_name} has already have type {error.channel_type.name} now."
            )
        else:
            _logger.error(error)
