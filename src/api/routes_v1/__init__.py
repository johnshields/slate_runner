from fastapi import APIRouter
from .projects import router as projects
from .assets import router as assets
from .shots import router as shots
from .tasks import router as tasks
from .versions import router as versions
from .publishes import router as publishes

router = APIRouter()
router.include_router(projects, tags=["projects"])
router.include_router(assets, tags=["assets"])
router.include_router(shots, tags=["shots"])
router.include_router(tasks, tags=["tasks"])
router.include_router(versions, tags=["versions"])
router.include_router(publishes, tags=["publishes"])
