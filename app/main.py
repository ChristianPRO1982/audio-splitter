from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.router import router as api_router
from app.core.config import settings
from app.storage.paths import StoragePaths


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    StoragePaths(data_dir=settings.data_dir).ensure_base_dirs()

    app = FastAPI(title=settings.app_name)
    app.include_router(api_router)

    app.mount("/assets", StaticFiles(directory="web", html=False), name="assets")

    @app.get("/")
    def index() -> FileResponse:
        """Serve the frontend entrypoint."""
        return FileResponse("web/index.html")

    return app


app = create_app()
