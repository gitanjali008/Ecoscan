import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.routes import router
from app.config import get_settings
from app.errors import register_error_handlers

logger = logging.getLogger(__name__)

# frontend/dist, made by `npm run build` in frontend/. Found from this file, not the
# working directory, so it works however uvicorn is started.
FRONTEND_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"


def create_app(frontend_dist: Path | None = FRONTEND_DIST) -> FastAPI:
    settings = get_settings()

    app = FastAPI(title=settings.app_name)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins.split(","),
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_error_handlers(app)
    app.include_router(router, prefix="/api")

    if frontend_dist is not None and frontend_dist.is_dir():
        serve_frontend(app, frontend_dist)
    else:
        logger.info(
            "No built frontend at %s, so only the API is served. "
            "Run `npm run build` in frontend/ to serve the app at /.",
            frontend_dist,
        )
    return app


def serve_frontend(app: FastAPI, dist: Path) -> None:
    """Serve the built frontend for any GET that no API route or docs page handles.

    It works as a 404 handler instead of a catch-all route, so routing is unchanged:
    /api, /docs and /openapi.json behave exactly as without a frontend.
    """
    dist = dist.resolve()

    async def frontend_or_404(request: Request, exc: StarletteHTTPException):
        path = request.url.path
        is_api = path == "/api" or path.startswith("/api/")
        if exc.status_code != 404 or request.method not in ("GET", "HEAD") or is_api:
            return await http_exception_handler(request, exc)

        file = (dist / path.lstrip("/")).resolve()
        # is_relative_to: "/../secret" must not escape the dist folder.
        if file.is_relative_to(dist) and file.is_file():
            return FileResponse(file)
        # A missing asset (e.g. an old /assets/app.js) stays a 404 instead of getting HTML.
        if Path(path).suffix:
            return await http_exception_handler(request, exc)
        # Any other page is the single-page app: index.html handles it.
        return FileResponse(dist / "index.html")

    app.add_exception_handler(StarletteHTTPException, frontend_or_404)


app = create_app()
