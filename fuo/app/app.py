import signal
from functools import partial

import anyio
from fastapi import FastAPI
from hypercorn.asyncio import serve
from hypercorn.config import Config

from .v1 import router as V1Router

description = """
User data api for FUO bot.

## v1
### user

* **Get user score**: Get the user's total score across all guilds (servers). Path `/v1/user/{user_id}/score`
* **Get user score logs**: Get score incoming logs of the user. Path `/v1/user/{user_id}/score/logs`
"""

app = FastAPI(title="FUO Bot API", description=description)

app.include_router(V1Router)


async def run_app(host: str, port: int):
    config = Config()
    config.bind = [f"{host}:{port}"]
    config.accesslog = "-"
    config.errorlog = "-"

    shutdown_event = anyio.Event()

    async def signal_handler():
        with anyio.open_signal_receiver(signal.SIGINT, signal.SIGTERM) as signals:
            async for _ in signals:
                shutdown_event.set()
                return

    async with anyio.create_task_group() as tg:
        tg.start_soon(signal_handler)

        serve_func = partial(serve, app, config, shutdown_trigger=shutdown_event.wait)  # type: ignore
        tg.start_soon(serve_func)
