from enum import Enum
from typing import Optional

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from fuo.db import Base

from .base import BaseMixin


class ScoreType(str, Enum):
    POST = "post"
    QUESTION = "question"
    CHAT = "chat"


class UserScore(Base, BaseMixin):
    __tablename__ = "user_scores"

    guild_id: Mapped[int] = mapped_column(sa.BigInteger, nullable=False, index=True)
    member_id: Mapped[int] = mapped_column(sa.BigInteger, nullable=False, index=True)
    score_type: Mapped[ScoreType] = mapped_column(
        sa.Enum(ScoreType), index=True, nullable=False
    )
    score: Mapped[float] = mapped_column(nullable=False, index=False, default=0)


class ScoreSource(str, Enum):
    POST = "post"
    POST_REACTION = "post_reaction"
    QUESTION = "question"
    ANSWER = "answer"
    ANSWER_REACTION = "answer_reaction"
    CHAT = "chat"
    CHAT_REACTION = "chat_reaction"


class ScoreConfig(Base, BaseMixin):
    __tablename__ = "score_configs"

    guild_id: Mapped[int] = mapped_column(sa.BigInteger, nullable=False, index=True)
    score_src: Mapped[ScoreSource] = mapped_column(
        sa.Enum(ScoreSource), nullable=False, index=True
    )
    score: Mapped[float] = mapped_column(nullable=False, index=True, default=0)

    channel_id: Mapped[Optional[int]] = mapped_column(
        sa.BigInteger, nullable=True, index=True, default=None
    )
    cooldown: Mapped[Optional[int]] = mapped_column(
        sa.Integer, nullable=True, index=False, default=None
    )


class ScoreLog(Base, BaseMixin):
    __tablename__ = "score_logs"

    guild_id: Mapped[int] = mapped_column(sa.BigInteger, nullable=False, index=True)
    channel_id: Mapped[int] = mapped_column(sa.BigInteger, nullable=False, index=True)
    member_id: Mapped[int] = mapped_column(sa.BigInteger, nullable=False, index=True)

    score_src: Mapped[ScoreSource] = mapped_column(
        sa.Enum(ScoreSource), nullable=False, index=True
    )
    score: Mapped[float] = mapped_column(nullable=False, index=False)


class ScoreSymbol(Base, BaseMixin):
    __tablename__ = "score_symbols"

    guild_id: Mapped[int] = mapped_column(sa.BigInteger, nullable=False, index=True)
    symbol: Mapped[str] = mapped_column(sa.String, nullable=False, index=False)
