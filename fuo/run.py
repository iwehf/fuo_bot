import anyio

from fuo import config
from fuo.app import run_app
from fuo.bot import run_bot


__all__ = ["run"]

async def _run():
    async with anyio.create_task_group() as tg:
        tg.start_soon(run_bot)
        tg.start_soon(run_app, config.app_host, config.app_port)


def run():
    try:
        anyio.run(_run)
    except KeyboardInterrupt:
        pass