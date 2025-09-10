from fastapi import APIRouter, Request, Depends
from api.system.system_service import status_payload, db_conn
from api.dependencies.auth import require_token, is_authenticated
from api.system.health_checker import get_health_status

router = APIRouter()


@router.get("/", summary="API status / load balancer check")
def api_root(request: Request):
    """Endpoint for LBs / uptime checks."""
    return status_payload(request.app)


@router.get("/authz", summary="Auth status")
def authz(request: Request):
    """Check whether the caller is authenticated."""
    return is_authenticated(request)


@router.get("/healthz", summary="Liveness")
def healthz(request: Request):
    """Health endpoint.
    - If caller is authenticated -> return full health status
    - If caller is not authenticated -> return minimal liveness
    """
    auth = is_authenticated(request)

    if auth.get("user_authenticated"):
        return get_health_status()

    return {"ok": True}


@router.get("/readyz", summary="Readiness", dependencies=[Depends(require_token)])
def readyz():
    """Check DB readiness."""
    return db_conn()
