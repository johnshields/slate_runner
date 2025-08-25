from fastapi import APIRouter
from .system import router as system

router = APIRouter()
router.include_router(system, tags=["system"])
