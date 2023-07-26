from typing import List, Optional

import discord
import sqlalchemy as sa
from anyio import create_task_group
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Annotated

from fuo import db, models

from .utils import OrderParam, get_channel, get_guild, get_user

router = APIRouter(prefix="/user")


class UserScore(BaseModel):
    score: float = Field(title="Score", description="User total score")


@router.get("/{user_id}/score", response_model=UserScore)
async def get_user_score(
    user: Annotated[discord.User, Depends(get_user)],
    type: Annotated[
        Optional[models.ScoreType],
        Query(
            title="Score type",
            description="Optional. Can be post, question or chat"
            "When score type is not set, means to get total score of all types.",
        ),
    ] = None,
    *,
    sess: Annotated[AsyncSession, Depends(db.get_session)],
) -> UserScore:
    q = sa.select(
        models.UserScore.member_id, sa.func.sum(models.UserScore.score).alias("sum")
    ).where(models.UserScore.member_id == user.id)
    if type is not None:
        q = q.where(models.UserScore.score_type == type)
    q = q.group_by(models.UserScore.member_id)

    res = (await sess.execute(q)).scalars().first()
    if res is None:
        return UserScore(score=0)

    return UserScore(score=res.sum)


class UserScoreLog(BaseModel):
    guild: str = Field(title="Guild (server)", description="Guild (server) name")
    channel: str = Field(title="Channel", description="Channel name")
    source: models.ScoreSource = Field(
        title="The reason of score",
        description="Where the incoming score comes from. "
        "Can be post, post_reaction, question, answer, answer_reaction, chat and chat_reaction.",
    )
    score: float = Field(title="Score", description="The incoming score.")


@router.get("/{user_id}/score/logs", response_model=List[UserScoreLog])
async def get_user_score_logs(
    user: Annotated[discord.User, Depends(get_user)],
    page: Annotated[
        int,
        Query(
            ge=1,
            title="Page",
            description="Optional. Default value is 1. Page should be greater than 1",
        ),
    ] = 1,
    page_size: Annotated[
        int,
        Query(
            ge=10,
            le=100,
            title="Page Size",
            description="Optional. Default value is 30. "
            "Page size should be greater than 10 and less than 100.",
        ),
    ] = 30,
    order: Annotated[
        OrderParam,
        Query(
            title="Order",
            description="Determine the order of the result logs. "
            "Optional. Default value is asc. Should be asc or desc.",
        ),
    ] = OrderParam.ASC,
    *,
    sess: Annotated[AsyncSession, Depends(db.get_session)],
) -> List[UserScoreLog]:
    q = (
        sa.select(models.ScoreLog)
        .where(models.ScoreLog.member_id == user.id)
        .limit(page_size)
        .offset((page - 1) * page_size)
    )
    if order == OrderParam.ASC:
        q = q.order_by(sa.asc(models.ScoreLog.id))
    else:
        q = q.order_by(sa.desc(models.ScoreLog.id))

    logs = (await sess.execute(q)).scalars().all()

    guild_ids = set(log.guild_id for log in logs)
    channel_ids = set(log.channel_id for log in logs)

    guild_names = {}

    async def _set_guild_name(guild_id: int):
        guild_names[guild_id] = (await get_guild(guild_id)).name

    async with create_task_group() as tg:
        for guild_id in guild_ids:
            tg.start_soon(_set_guild_name, guild_id)

    channel_names = {}

    async def _set_channel_name(channel_id: int):
        channel_names[channel_id] = (await get_channel(channel_id)).name

    async with create_task_group() as tg:
        for channel_id in channel_ids:
            tg.start_soon(_set_channel_name, channel_id)

    res = [
        UserScoreLog(
            guild=guild_names[log.guild_id],
            channel=channel_names[log.channel_id],
            source=log.score_src,
            score=log.score,
        )
        for log in logs
    ]
    return res
