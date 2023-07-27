import anyio

from fuo import config, db, log
from fuo.app import run_app
from fuo.bot import run_bot


__all__ = ["run"]

async def _run():
    log.init()
    await db.init()
    try:
        async with anyio.create_task_group() as tg:
            tg.start_soon(run_bot)
            tg.start_soon(run_app, config.app_host, config.app_port)
    finally:
        await db.close()

def run():
    try:
        anyio.run(_run)
    except KeyboardInterrupt:
        pass