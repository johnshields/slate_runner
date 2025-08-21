from fastapi import APIRouter, Request
from api.service import status_payload, db_conn

router = APIRouter()


@router.get("/", summary="API status / load balancer check")
def api_root(request: Request):
    """Endpoint for LBs / uptime checks."""
    return status_payload(request.app)


@router.get("/healthz", summary="Liveness")
def healthz():
    """Health endpoint."""
    return {"ok": True}


@router.get("/readyz", summary="Readiness")
def readyz():
    """Check DB readiness."""
    return db_conn()
