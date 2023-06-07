from __future__ import annotations

import threading
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Callable, Coroutine, TypeVar

from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    async_sessionmaker, create_async_engine)
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass
from typing_extensions import ParamSpec

from fuo import config

__all__ = ["session_scope", "init", "close", "Base", "get_session", "use_session"]

_local = threading.local()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    if (not hasattr(_local, "session")) or (not hasattr(_local, "engine")):
        raise ValueError("db has not been initialized")
    session: async_sessionmaker[AsyncSession] = _local.session
    async with session() as sess:
        try:
            yield sess
        except:
            await sess.rollback()
            raise


session_scope = asynccontextmanager(get_session)


_P = ParamSpec("_P")
_T = TypeVar("_T")


def use_session(
    func: Callable[_P, Coroutine[None, None, _T]]
) -> Callable[_P, Coroutine[None, None, _T]]:
    async def inner(*args: _P.args, **kwargs: _P.kwargs) -> _T:
        sess = kwargs.pop("sess", None)
        if sess is None:
            async with session_scope() as sess:
                kwargs["sess"] = sess
                res = await func(*args, **kwargs)
        else:
            kwargs["sess"] = sess
            res = await func(*args, **kwargs)
        return res

    return inner


class Base(DeclarativeBase, MappedAsDataclass):
    pass


async def init(db: str = config.db):
    if hasattr(_local, "session") or hasattr(_local, "engine"):
        raise ValueError("db has been initialized")

    engine = create_async_engine(
        db,
        pool_pre_ping=True,
        # echo=True,
    )
    session = async_sessionmaker(engine, autoflush=False, expire_on_commit=False)

    _local.engine = engine
    _local.session = session


async def close():
    if (not hasattr(_local, "session")) or (not hasattr(_local, "engine")):
        raise ValueError("db has not been initialized")

    engine: AsyncEngine = _local.engine
    await engine.dispose()

    delattr(_local, "engine")
    delattr(_local, "session")
