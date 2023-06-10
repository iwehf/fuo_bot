from __future__ import annotations

import logging
from datetime import datetime, timezone

import discord
from discord.ext import commands

from fuo import models, utils

from .channel_cog import ChannelCog
from .score_cog import ScoreCog

_logger = logging.getLogger(__name__)


class PostCog(commands.Cog, name="post"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def _get_score_cog(self) -> ScoreCog:
        score_cog = self.bot.get_cog("score")
        assert score_cog is not None
        assert isinstance(score_cog, ScoreCog)
        return score_cog

    def _get_channel_cog(self) -> ChannelCog:
        channel_cog = self.bot.get_cog("channel")
        assert channel_cog is not None
        assert isinstance(channel_cog, ChannelCog)
        return channel_cog

    async def _in_post_channel(self, guild_id: int, channel_id: int) -> int:
        channel_cog = self._get_channel_cog()
        return await channel_cog.check_channel_type(
            guild_id=guild_id,
            channel_id=channel_id,
            channel_type=models.ChannelType.POST,
        )

    @commands.Cog.listener(name="on_message")
    async def post_message(self, message: discord.Message):
        try:
            assert message.guild is not None
            assert isinstance(message.author, discord.Member)

            guild_id = message.guild.id
            member_id = message.author.id
            channel_id = message.channel.id

            if (
                not utils.is_bot(self.bot, message)
                and not await utils.is_command(self.bot, message)
                and await self._in_post_channel(
                    guild_id=guild_id, channel_id=channel_id
                )
            ):
                score_cog = self._get_score_cog()
                await score_cog.post_score(guild_id=guild_id, member_id=member_id)

                _logger.info(
                    f"author {message.author.name}, post in message {message.id}"
                )
        except Exception as e:
            _logger.error(e)
            raise

    @commands.Cog.listener(name="on_raw_reaction_add")
    async def reaction_on_post(self, payload: discord.RawReactionActionEvent):
        try:
            assert payload.member is not None
            assert payload.guild_id is not None
            emoji = payload.emoji.name
            if not utils.is_valid_emoji(emoji):
                return

            if await self._in_post_channel(
                guild_id=payload.guild_id, channel_id=payload.channel_id
            ):
                channel = self.bot.get_channel(payload.channel_id)
                assert isinstance(channel, discord.TextChannel)

                message = await channel.fetch_message(payload.message_id)

                delta = datetime.now(timezone.utc) - message.created_at
                if delta.days < 1:
                    score_cog = self._get_score_cog()
                    await score_cog.post_reaction_score(
                        guild_id=payload.guild_id,
                        member_id=payload.member.id,
                    )
        except Exception as e:
            _logger.error(e)
            raise
