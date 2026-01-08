from fastapi import APIRouter

from app.api.routes.health import router as health_router
from app.api.routes.projects import router as projects_router
from app.api.routes.media import router as media_router
from app.api.routes.cuts import router as cuts_router
from app.api.routes.cleanup import router as cleanup_router

router = APIRouter(prefix="/api")
router.include_router(health_router, tags=["health"])
router.include_router(projects_router, tags=["projects"])
router.include_router(media_router, tags=["media"])
router.include_router(cuts_router, tags=["cuts"])
router.include_router(cleanup_router, tags=["cleanup"])
