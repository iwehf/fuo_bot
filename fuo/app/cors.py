from fastapi.middleware.cors import CORSMiddleware
from typing import TYPE_CHECKING

from fuo import config

if TYPE_CHECKING:
    from fastapi import FastAPI

def enable_cors(app: FastAPI):
    app.add_middleware(
        CORSMiddleware, 
        allow_origins=config.allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
