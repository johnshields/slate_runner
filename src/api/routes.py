from fastapi import APIRouter, Request
from api.service import status_payload

router = APIRouter()


@router.get("/", summary="API status / load balancer check")
def api_root(request: Request):
    """
    Lightweight health endpoint for LBs / uptime checks.
    """
    return status_payload(request.app)
