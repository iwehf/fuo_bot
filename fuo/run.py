import signal

import anyio

from fuo import config, db, log
from fuo.app import App
from fuo.bot import run_bot

__all__ = ["run"]

async def _run():
    log.init()
    await db.init()
    try:
        async with anyio.create_task_group() as tg:
            app = App()

            async def signal_handler():
                with anyio.open_signal_receiver(signal.SIGINT, signal.SIGTERM) as signals:
                    async for _ in signals:
                        app.stop()
                        tg.cancel_scope.cancel()
                        return

            tg.start_soon(signal_handler)

            tg.start_soon(run_bot)
            tg.start_soon(app.run, config.app_host, config.app_port)
    finally:
        await db.close()

def run():
    try:
        anyio.run(_run)
    except KeyboardInterrupt:
        pass