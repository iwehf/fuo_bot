from functools import partial

import anyio
from fastapi import FastAPI
from hypercorn.asyncio import serve
from hypercorn.config import Config

from .cors import enable_cors
from .v1 import router as V1Router

description = """
User data api for FUO bot.

## v1
### user

* **Get user score**: Get the user's total score across all guilds (servers). Path `/v1/user/{user_id}/score`
* **Get user score logs**: Get score incoming logs of the user. Path `/v1/user/{user_id}/score/logs`
"""



class App(object):
    def __init__(self) -> None:
        self._app = FastAPI(title="FUO Bot API", description=description)
        self._app.include_router(V1Router)
        enable_cors(app=self._app)

        self._shutdown_event = anyio.Event()

    async def run(self, host: str, port: int):
        config = Config()
        config.bind = [f"{host}:{port}"]
        config.accesslog = "-"
        config.errorlog = "-"

        async with anyio.create_task_group() as tg:
            serve_func = partial(serve, self._app, config, shutdown_trigger=self._shutdown_event.wait)  # type: ignore
            tg.start_soon(serve_func)

    def stop(self):
        self._shutdown_event.set()
