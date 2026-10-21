from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import root_router, router
from app.config import get_settings
from app.errors import register_error_handlers


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(title=settings.app_name)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins.split(","),
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_error_handlers(app)
    app.include_router(root_router)
    app.include_router(router, prefix="/api")
    return app


app = create_app()
