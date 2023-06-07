from __future__ import annotations

import logging

import discord
from discord.ext import commands

from fuo import model, utils

from .channel_cog import ChannelCog
from .score_cog import ScoreCog

_logger = logging.getLogger(__name__)


class ChatCog(commands.Cog, name="chat"):
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

    async def _in_chat_channel(self, guild_id: int, channel_id: int) -> int:
        channel_cog = self._get_channel_cog()
        return await channel_cog.check_channel_type(
            guild_id=guild_id,
            channel_id=channel_id,
            channel_type=model.ChannelType.CHAT,
        )

    @commands.Cog.listener(name="on_message")
    async def chat_message(self, message: discord.Message):
        try:
            assert message.guild is not None
            assert isinstance(message.author, discord.Member)

            guild_id = message.guild.id
            member_id = message.author.id
            channel_id = message.channel.id

            if not await utils.is_command(
                self.bot, message
            ) and await self._in_chat_channel(guild_id=guild_id, channel_id=channel_id):
                score_cog = self._get_score_cog()
                await score_cog.chat_score(
                    guild_id=guild_id, channel_id=channel_id, member_id=member_id
                )

                _logger.info(
                    f"author {message.author.name}, chat in message {message.id}"
                )
        except Exception as e:
            _logger.error(e)
            raise

    @commands.Cog.listener(name="on_raw_reaction_add")
    async def reaction_on_chat(self, payload: discord.RawReactionActionEvent):
        try:
            assert payload.member is not None
            assert payload.guild_id is not None
            emoji = payload.emoji.name
            if not utils.is_valid_emoji(emoji):
                return

            if await self._in_chat_channel(
                guild_id=payload.guild_id, channel_id=payload.channel_id
            ):
                score_cog = self._get_score_cog()
                await score_cog.chat_reaction_score(
                    guild_id=payload.guild_id,
                    channel_id=payload.channel_id,
                    member_id=payload.member.id,
                )
        except Exception as e:
            _logger.error(e)
            raise
