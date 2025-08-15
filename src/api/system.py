from fastapi import APIRouter, Request
from api.service import status_payload, db_conn

router = APIRouter()


@router.get("/", summary="API status / load balancer check")
def api_root(request: Request):
    """Lightweight health endpoint for LBs / uptime checks."""
    return status_payload(request.app)


@router.get("/healthz", summary="Liveness")
def healthz():
    return {"ok": True}


@router.get("/readyz", summary="Readiness (DB ping)")
def readyz():
    """Check DB readiness."""
    return db_conn()
