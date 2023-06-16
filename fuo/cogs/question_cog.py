from __future__ import annotations

import asyncio
import logging

import discord
import sqlalchemy as sa
from discord.ext import commands
from tabulate import tabulate

from fuo import config, db, models, utils

from .channel_cog import ChannelCog
from .score_cog import ScoreCog

_logger = logging.getLogger(__name__)


class QuestionFinished(commands.CommandError):
    pass


class QuestionNotFinished(commands.CommandError):
    pass


class QuestionMissing(commands.CommandError):
    pass


def question_summary(guild: discord.Guild, question: models.Question) -> discord.Embed:
    rows = []
    for answer in question.answers:
        member = guild.get_member(answer.member_id)
        if member is not None:
            rows.append(
                {
                    "name": member.name,
                    "like": answer.like,
                    "dislike": answer.dislike,
                }
            )

    table = tabulate(rows, headers="keys", tablefmt="pretty")

    embed = discord.Embed(
        color=discord.Color.from_str(config.info_color),
        title="Close the question successfully.",
    )
    embed.add_field(name="Answers count", value=len(question.answers), inline=False)
    embed.add_field(name="Answers detail", value=f"```{table}```", inline=False)

    return embed


class QuestionCog(commands.Cog, name="question"):
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

    async def in_question_channel(self, guild_id: int, channel_id: int) -> bool:
        channel_cog = self._get_channel_cog()
        return await channel_cog.check_channel_type(
            guild_id=guild_id,
            channel_id=channel_id,
            channel_type=models.ChannelType.QUESTION,
        )

    async def cog_check(self, ctx: commands.Context) -> bool:
        if ctx.guild is not None:
            guild_id = ctx.guild.id
            channel_id = ctx.channel.id
            return await self.in_question_channel(
                guild_id=guild_id, channel_id=channel_id
            )
        else:
            return False

    @commands.command(name="question", help="Ask a question")
    @commands.has_role(config.discord_role)
    async def ask_question(self, ctx: commands.Context):
        assert ctx.guild is not None
        assert isinstance(ctx.author, discord.Member)

        guild_id = ctx.guild.id
        channel_id = ctx.channel.id
        member_id = ctx.author.id

        async with db.session_scope() as sess:
            q = (
                sa.select(models.Question)
                .where(models.Question.guild_id == guild_id)
                .where(models.Question.channel_id == channel_id)
                .order_by(sa.desc(models.Question.id))
                .limit(1)
            )

            last_question = (await sess.execute(q)).scalars().first()
            if last_question is not None and last_question.opened:
                raise QuestionNotFinished

            question = models.Question(
                guild_id=guild_id,
                member_id=member_id,
                channel_id=channel_id,
            )
            sess.add(question)
            await sess.commit()

        embed = discord.Embed(
            color=discord.Color.from_str(config.success_color),
            title="Ask a question successfully",
            description=f"{ctx.author.mention} ask a question.",
        )
        await ctx.send(embed=embed)

    @ask_question.error
    async def ask_question_error(self, ctx: commands.Context, error: Exception):
        _logger.error(error)
        embed = discord.Embed(
            color=discord.Color.from_str(config.error_color), title="Error!"
        )
        if isinstance(error, commands.MissingRole):
            embed.description = "Sorry, you are not permitted to execute this command."
        elif isinstance(error, commands.BadArgument):
            embed.description = f"Sorry, {str(error)}"
        elif isinstance(error, QuestionNotFinished):
            embed.description = (
                "Last question is not closed yet! "
                "You should close the last question first and then ask a new question."
            )
        else:
            embed.description = "Sorry, there's sth wrong with FUO bot."
        await ctx.send(embed=embed)

    @commands.command(name="answer", help="Answer the last question")
    async def answer_question(self, ctx: commands.Context):
        assert ctx.guild is not None
        assert isinstance(ctx.author, discord.Member)

        guild_id = ctx.guild.id
        channel_id = ctx.channel.id
        member_id = ctx.author.id

        async with db.session_scope() as sess:
            q = (
                sa.select(models.Question)
                .where(models.Question.guild_id == guild_id)
                .where(models.Question.channel_id == channel_id)
                .order_by(sa.desc(models.Question.id))
                .limit(1)
            )

            question = (await sess.execute(q)).scalars().first()
            if question is None:
                raise QuestionMissing
            if not question.opened:
                raise QuestionFinished
            question_author = self.bot.get_user(question.member_id)

            answer = models.Answer(
                guild_id=guild_id,
                member_id=member_id,
                channel_id=channel_id,
                question_id=question.id,
                message_id=ctx.message.id,
            )
            sess.add(answer)
            await sess.commit()

        embed = discord.Embed(
            color=discord.Color.from_str(config.success_color),
            title="Answer the question successfully",
        )
        if question_author is not None:
            embed.description = f"{ctx.author.mention} answer the question asked by {question_author.mention}."
        else:
            embed.description = f"{ctx.author.mention} answer the question"
        await ctx.send(embed=embed)

    @answer_question.error
    async def answer_question_error(self, ctx: commands.Context, error: Exception):
        _logger.error(error)
        embed = discord.Embed(
            color=discord.Color.from_str(config.error_color), title="Error!"
        )
        if isinstance(error, commands.MissingRole):
            embed.description = "Sorry, you are not permitted to execute this command."
        elif isinstance(error, commands.BadArgument):
            embed.description = f"Sorry, {str(error)}"
        elif isinstance(error, QuestionMissing):
            embed.description = "Question is not found! Cannot answer it."
        elif isinstance(error, QuestionFinished):
            embed.description = (
                "The question has been already closed! Cannot answer it twice."
            )
        else:
            embed.description = "Sorry, there's sth wrong with FUO bot."
        await ctx.send(embed=embed)

    @commands.command(
        name="close-question",
        help="Alose a question. A closed question cannot be answered",
    )
    @commands.has_role(config.discord_role)
    async def close_question(self, ctx: commands.Context):
        assert ctx.guild is not None
        assert isinstance(ctx.author, discord.Member)

        guild_id = ctx.guild.id
        channel_id = ctx.channel.id

        async with db.session_scope() as sess:
            q = (
                sa.select(models.Question)
                .where(models.Question.guild_id == guild_id)
                .where(models.Question.channel_id == channel_id)
                .order_by(sa.desc(models.Question.id))
                .limit(1)
            )

            question = (await sess.execute(q)).scalars().first()
            if question is None:
                raise QuestionMissing
            if not question.opened:
                raise QuestionFinished

            await sess.refresh(question, ["answers"])
            question.answers.sort(key=lambda answer: answer.like, reverse=True)

            summary = question_summary(ctx.guild, question)

            question.opened = False

            score_cog = self._get_score_cog()
            await score_cog.question_score(
                guild_id=guild_id,
                channel_id=channel_id,
                member_id=question.member_id,
                sess=sess,
            )
            futs = []
            for answer in question.answers:
                fut = score_cog.answer_score(
                    guild_id=guild_id,
                    channel_id=channel_id,
                    member_id=answer.member_id,
                    like=answer.like,
                    dislike=answer.dislike,
                    sess=sess,
                )
                futs.append(fut)
            await asyncio.wait(futs)

            await sess.commit()

        await ctx.send(embed=summary)

    @close_question.error
    async def close_question_error(self, ctx: commands.Context, error: Exception):
        _logger.error(error)
        embed = discord.Embed(
            color=discord.Color.from_str(config.error_color), title="Error!"
        )
        if isinstance(error, commands.MissingRole):
            embed.description = "Sorry, you are not permitted to execute this command."
        elif isinstance(error, commands.BadArgument):
            embed.description = f"Sorry, {str(error)}"
        elif isinstance(error, QuestionMissing):
            embed.description = "Question is not found! Cannot close it."
        elif isinstance(error, QuestionFinished):
            embed.description = (
                "The question has been already closed! Cannot close it twice."
            )
        else:
            embed.description = "Sorry, there's sth wrong with FUO bot."
        await ctx.send(embed=embed)

    @commands.Cog.listener(name="on_raw_reaction_add")
    async def reaction_on_answer(self, payload: discord.RawReactionActionEvent):
        try:
            assert payload.member is not None
            assert payload.guild_id is not None
            emoji = payload.emoji.name
            if not utils.is_valid_emoji(emoji):
                return

            if await self.in_question_channel(
                guild_id=payload.guild_id, channel_id=payload.channel_id
            ):
                async with db.session_scope() as sess:
                    q = (
                        sa.select(models.Answer)
                        .where(models.Answer.guild_id == payload.guild_id)
                        .where(models.Answer.channel_id == payload.channel_id)
                        .where(models.Answer.message_id == payload.message_id)
                    )

                    answer = (await sess.execute(q)).scalar_one_or_none()
                    if answer is not None:
                        if utils.is_like_emoji(emoji):
                            answer.like += 1
                            _logger.info(f"answer {payload.message_id} has been liked")
                        elif utils.is_dislike_emoji(emoji):
                            answer.dislike += 1
                            _logger.info(
                                f"answer {payload.message_id} has been disliked"
                            )

                        await sess.commit()
        except Exception as e:
            _logger.error(e)
            raise
