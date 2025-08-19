from fastapi import APIRouter
from .projects import router as projects
from .assets import router as assets

router = APIRouter()
router.include_router(projects, tags=["projects"])
router.include_router(assets, tags=["assets"])
