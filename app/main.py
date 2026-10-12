from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import __version__
from app.api.router import router
from app.core.config import Settings
from app.core.errors import register_error_handlers


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    application.state.started = True
    try:
        yield
    finally:
        application.state.started = False


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings if settings is not None else Settings()
    application = FastAPI(
        title=settings.app_name,
        description="BriefPilot evidence-grounded product research API",
        version=__version__,
        lifespan=lifespan,
    )
    application.state.settings = settings
    application.state.started = False
    register_error_handlers(application)
    application.include_router(router)
    return application


app = create_app()
