from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fuo import config


def enable_cors(app: FastAPI):
    app.add_middleware(
        CORSMiddleware, 
        allow_origins=config.allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
