from __future__ import annotations

import logging
from collections import defaultdict
from typing import DefaultDict, Optional, Tuple
from typing_extensions import Annotated

import discord
import sqlalchemy as sa
from discord.ext import commands
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Annotated

from fuo import config, db, models, utils

_logger = logging.getLogger(__name__)


class ScoreCog(commands.Cog, name="score"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.score_configs: DefaultDict[
            models.ScoreSource, DefaultDict[int | Tuple[int, int], float]
        ] = defaultdict(lambda: defaultdict(lambda: 1.0))

    async def _get_action_score(
        self,
        score_src: models.ScoreSource,
        guild_id: int,
        channel_id: Optional[int] = None,
        *,
        sess: AsyncSession | None = None,
    ) -> float:
        assert sess is not None

        score_config = self.score_configs[score_src]
        if channel_id is None:
            score_key = guild_id
        else:
            score_key = (guild_id, channel_id)

        # first find config for the specific score source and channel,
        # then find config for the specific score source only,
        if score_key in score_config:
            score = score_config[score_key]
        elif guild_id in score_config:
            score = score_config[guild_id]
        else:
            conf = None
            if channel_id is not None:
                q = (
                    sa.select(models.ScoreConfig)
                    .where(models.ScoreConfig.guild_id == guild_id)
                    .where(models.ScoreConfig.score_src == score_src)
                    .where(models.ScoreConfig.channel_id == channel_id)
                )
                conf = (await sess.execute(q)).scalar_one_or_none()
            if conf is not None:
                score = conf.score
                score_config[score_key] = score
            else:
                q = (
                    sa.select(models.ScoreConfig)
                    .where(models.ScoreConfig.guild_id == guild_id)
                    .where(models.ScoreConfig.score_src == score_src)
                )
                conf = (await sess.execute(q)).scalar_one_or_none()
                if conf is not None:
                    score = conf.score
                    score_config[guild_id] = score
                else:
                    score = score_config[score_key]

        return score

    @db.use_session
    async def _add_member_score(
        self,
        guild_id: int,
        member_id: int,
        score: float,
        score_type: models.ScoreType,
        *,
        sess: AsyncSession | None = None,
    ):
        assert sess is not None
        q = (
            sa.select(models.UserScore)
            .where(models.UserScore.guild_id == guild_id)
            .where(models.UserScore.member_id == member_id)
            .where(models.UserScore.score_type == score_type)
        )
        record = (await sess.execute(q)).scalar_one_or_none()
        if record is not None:
            record.score += score
        else:
            record = models.UserScore(
                guild_id=guild_id,
                member_id=member_id,
                score=score,
                score_type=score_type,
            )
            sess.add(record)
        await sess.commit()

    @db.use_session
    async def post_score(
        self,
        guild_id: int,
        channel_id: int,
        member_id: int,
        *,
        sess: AsyncSession | None = None,
    ):
        assert sess is not None

        score = await self._get_action_score(
            guild_id=guild_id,
            channel_id=channel_id,
            score_src=models.ScoreSource.POST,
            sess=sess,
        )
        await self._add_member_score(
            guild_id=guild_id,
            member_id=member_id,
            score=score,
            score_type=models.ScoreType.POST,
            sess=sess,
        )
        _logger.info(f"add {score} post score to member {member_id}")

    @db.use_session
    async def post_reaction_score(
        self,
        guild_id: int,
        channel_id: int,
        member_id: int,
        *,
        sess: AsyncSession | None = None,
    ):
        assert sess is not None

        score = await self._get_action_score(
            guild_id=guild_id,
            channel_id=channel_id,
            score_src=models.ScoreSource.POST_REACTION,
            sess=sess,
        )
        await self._add_member_score(
            guild_id=guild_id,
            member_id=member_id,
            score=score,
            score_type=models.ScoreType.POST,
            sess=sess,
        )
        _logger.info(f"add {score} post reaction score to member {member_id}")

    @db.use_session
    async def chat_score(
        self,
        guild_id: int,
        channel_id: int,
        member_id: int,
        *,
        sess: AsyncSession | None = None,
    ):
        assert sess is not None

        score = await self._get_action_score(
            guild_id=guild_id,
            channel_id=channel_id,
            score_src=models.ScoreSource.CHAT,
            sess=sess,
        )
        await self._add_member_score(
            guild_id=guild_id,
            member_id=member_id,
            score=score,
            score_type=models.ScoreType.CHAT,
            sess=sess,
        )
        _logger.info(f"add {score} chat score to member {member_id}")

    @db.use_session
    async def chat_reaction_score(
        self,
        guild_id: int,
        channel_id: int,
        member_id: int,
        *,
        sess: AsyncSession | None = None,
    ):
        assert sess is not None

        score = await self._get_action_score(
            guild_id=guild_id,
            channel_id=channel_id,
            score_src=models.ScoreSource.CHAT_REACTION,
            sess=sess,
        )
        await self._add_member_score(
            guild_id=guild_id,
            member_id=member_id,
            score=score,
            score_type=models.ScoreType.CHAT,
            sess=sess,
        )
        _logger.info(f"add {score} chat reaction score to member {member_id}")

    @db.use_session
    async def question_score(
        self,
        guild_id: int,
        channel_id: int,
        member_id: int,
        *,
        sess: AsyncSession | None = None,
    ):
        assert sess is not None

        score = await self._get_action_score(
            guild_id=guild_id,
            channel_id=channel_id,
            score_src=models.ScoreSource.QUESTION,
            sess=sess,
        )
        await self._add_member_score(
            guild_id=guild_id,
            member_id=member_id,
            score=score,
            score_type=models.ScoreType.QUESTION,
            sess=sess,
        )
        _logger.info(f"add {score} question score to member {member_id}")

    @db.use_session
    async def answer_score(
        self,
        guild_id: int,
        channel_id: int,
        member_id: int,
        like: int,
        dislike: int,
        *,
        sess: AsyncSession | None = None,
    ):
        assert sess is not None

        answer_score = await self._get_action_score(
            guild_id=guild_id,
            channel_id=channel_id,
            score_src=models.ScoreSource.ANSWER,
            sess=sess,
        )
        answer_reation_score_base = await self._get_action_score(
            guild_id=guild_id,
            channel_id=channel_id,
            score_src=models.ScoreSource.ANSWER_REACTION,
            sess=sess,
        )
        answer_reaction_score = answer_reation_score_base * (like - dislike)

        score = answer_score + answer_reaction_score
        await self._add_member_score(
            guild_id=guild_id,
            member_id=member_id,
            score=score,
            score_type=models.ScoreType.QUESTION,
            sess=sess,
        )
        _logger.info(f"add {score} answer score to member {member_id}")

    @commands.command(
        name="get-score",
        help="Get a member's score of the specified type. "
        "Score types can be POST, QUESTION or CHAT.",
    )
    @commands.has_role(config.discord_role)
    async def get_member_score(
        self,
        ctx: commands.Context,
        member: discord.Member,
        score_type: Annotated[models.ScoreType, utils.to_score_type],
    ):
        async with db.session_scope() as sess:
            q = (
                sa.select(models.UserScore)
                .where(models.UserScore.guild_id == member.guild.id)
                .where(models.UserScore.member_id == member.id)
                .where(models.UserScore.score_type == score_type)
            )
            user_score = (await sess.execute(q)).scalar_one_or_none()
            if user_score is None:
                score = 0
            else:
                score = user_score.score

        await ctx.send(f"member {member.name} current {score_type.name} score: {score}")

    @commands.command(
        name="add-score",
        help="Manually add some score of the specified type to a member. "
        "Score types can be POST, QUESTION or CHAT.",
    )
    @commands.has_role(config.discord_role)
    async def manual_add_score(
        self,
        ctx: commands.Context,
        member: discord.Member,
        score_type: Annotated[models.ScoreType, utils.to_score_type],
        score: float,
    ):
        await self._add_member_score(
            guild_id=member.guild.id,
            member_id=member.id,
            score=score,
            score_type=score_type,
        )
        await ctx.send(f"add {score} score to member {member.name}")

    async def cog_command_error(self, ctx: commands.Context, error: Exception):
        _logger.error(error)

    @commands.command(
        name="set-action-score",
        help="Set reward score of the specific action. "
        "Action type can be POST, POST_REACTION, QUESTION, ANSWER, "
        "ANSWER_REACTION, CHAT, CHAT_REACTION",
    )
    @commands.has_role(config.discord_role)
    async def set_action_score(
        self,
        ctx: commands.Context,
        score_src: Annotated[models.ScoreSource, utils.to_score_source],
        channel: Optional[discord.TextChannel] = None,
        *,
        score: float,
    ):
        assert ctx.guild is not None
        guild_id = ctx.guild.id

        async with db.session_scope() as sess:
            q = (
                sa.select(models.ScoreConfig)
                .where(models.ScoreConfig.guild_id == guild_id)
                .where(models.ScoreConfig.score_src == score_src)
            )
            if channel is not None:
                q = q.where(models.ScoreConfig.channel_id == channel.id)
            conf = (await sess.execute(q)).scalar_one_or_none()
            if conf is not None:
                conf.score = score
            else:
                conf = models.ScoreConfig(
                    guild_id=guild_id,
                    score_src=score_src,
                    score=score,
                )
                if channel is not None:
                    conf.channel_id = channel.id
                sess.add(conf)
            await sess.commit()

        # update local score config
        if channel is not None:
            score_key = (guild_id, channel.id)
        else:
            score_key = guild_id

        self.score_configs[score_src][score_key] = score

        channel_name = channel.name if channel is not None else "all"
        _logger.info(
            f"guild {ctx.guild.name} set action {score_src.name} of {channel_name} channel {score} scores"
        )

    @commands.command(
        name="get-action-score",
        help="Get reward score of the specific action. "
        "Action type can be POST, POST_REACTION, QUESTION, ANSWER, "
        "ANSWER_REACTION, CHAT, CHAT_REACTION",
    )
    @commands.has_role(config.discord_role)
    async def get_action_score(
        self,
        ctx: commands.Context,
        score_src: Annotated[models.ScoreSource, utils.to_score_source],
        channel: Optional[discord.TextChannel] = None,
    ):
        assert ctx.guild is not None
        guild_id = ctx.guild.id

        async with db.session_scope() as sess:
            channel_id = channel.id if channel is not None else None
            score = await self._get_action_score(
                score_src=score_src, guild_id=guild_id, channel_id=channel_id, sess=sess
            )

        channel_name = channel.name if channel is not None else "all"
        await ctx.send(
            f"action {score_src.name} score of {channel_name} channel: {score}"
        )
