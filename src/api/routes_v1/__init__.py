from fastapi import APIRouter
from .projects import router as projects

router = APIRouter()
router.include_router(projects, tags=["projects"])
