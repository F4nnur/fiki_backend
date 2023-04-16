from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.config import settings
from src.db import session_manager


def init_app(init_db=True):
    lifespan = None

    if init_db:
        session_manager.init(settings.DB_URL)

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            yield
            if session_manager._engine is not None:
                await session_manager.close()

    server = FastAPI(title="My FastAPI Server", lifespan=lifespan)

    return server


server = init_app()
