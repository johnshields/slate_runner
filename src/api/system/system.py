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
def authz(auth=Depends(require_token)):
    """Check whether the caller is authenticated + role info."""
    return auth


@router.get("/healthz", summary="Liveness")
def healthz(auth=Depends(require_token)):
    """Health endpoint.
    - If caller is authenticated -> return full health status
    - If caller is not authenticated -> return minimal liveness
    """
    if auth.get("user_authenticated"):
        return get_health_status()
    return {"ok": True}


@router.get("/readyz", summary="Readiness", dependencies=[Depends(require_token)])
def readyz():
    """Check DB readiness (only authenticated users)."""
    return db_conn()
