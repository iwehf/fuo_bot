from enum import IntEnum

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from fuo.db import Base

from .base import BaseMixin


class ChannelType(IntEnum):
    POST = 0
    QUESTION = 1
    CHAT = 2


class ChannelConfig(Base, BaseMixin):
    __tablename__ = "channel_configs"

    guild_id: Mapped[int] = mapped_column(sa.BigInteger, nullable=False, index=True)
    channel_id: Mapped[int] = mapped_column(sa.BigInteger, nullable=False, index=True)
    channel_type: Mapped[ChannelType] = mapped_column(
        sa.Enum(ChannelType), nullable=False, index=False
    )
