from typing import List

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fuo.db import Base

from .base import BaseMixin


class Question(Base, BaseMixin):
    __tablename__ = "questions"

    guild_id: Mapped[int] = mapped_column(sa.BigInteger, nullable=False, index=True)
    member_id: Mapped[int] = mapped_column(sa.BigInteger, nullable=False, index=True)
    channel_id: Mapped[int] = mapped_column(sa.BigInteger, nullable=False, index=True)
    opened: Mapped[bool] = mapped_column(nullable=False, index=False, default=True)

    answers: Mapped[List["Answer"]] = relationship(
        "Answer",
        primaryjoin="foreign(Answer.question_id) == Question.id",
        back_populates="question",
        init=False,
        default_factory=list,
    )


class Answer(Base, BaseMixin):
    __tablename__ = "answers"

    guild_id: Mapped[int] = mapped_column(sa.BigInteger, nullable=False, index=True)
    member_id: Mapped[int] = mapped_column(sa.BigInteger, nullable=False, index=True)
    channel_id: Mapped[int] = mapped_column(sa.BigInteger, nullable=False, index=True)
    message_id: Mapped[int] = mapped_column(sa.BigInteger, nullable=False, index=False)
    question_id: Mapped[int] = mapped_column(nullable=False, index=True)

    like: Mapped[int] = mapped_column(nullable=False, index=False, default=0)
    dislike: Mapped[int] = mapped_column(nullable=False, index=False, default=0)

    question: Mapped[Question] = relationship(
        "Question",
        primaryjoin="foreign(Answer.question_id) == Question.id",
        back_populates="answers",
        init=False,
        default=None,
    )
