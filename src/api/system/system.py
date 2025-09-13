from fastapi import APIRouter, Request, Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from api.system.system_service import status_payload, db_conn
from api.dependencies.auth import require_token, is_authenticated
from api.system.health_checker import get_health_status
from db.db import get_db

router = APIRouter()
bearer = HTTPBearer(auto_error=False)


@router.get("/", summary="API status / load balancer check")
def api_root(request: Request):
    """Endpoint for LBs / uptime checks."""
    return status_payload(request.app)


@router.get("/authz", summary="Auth status")
def authz(auth=Depends(require_token)):
    """Check whether the caller is authenticated + role info."""
    return auth


@router.get("/healthz", summary="Liveness")
def healthz(
        db: Session = Depends(get_db),
        credentials: HTTPAuthorizationCredentials = Security(bearer),
):
    """
    Health endpoint.
    - If caller is authenticated -> return full health status
    - If caller is not authenticated -> return minimal liveness
    """
    if not credentials:
        return {"ok": True}

    try:
        auth = require_token(credentials=credentials, db=db)
        if auth.get("user_authenticated"):
            return get_health_status()
    except HTTPException:
        return {"ok": True}

    return {"ok": True}


@router.get("/readyz", summary="Readiness", dependencies=[Depends(require_token)])
def readyz():
    """Check DB readiness (only authenticated users)."""
    return db_conn()
