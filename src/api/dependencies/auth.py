from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import text
from db.db import get_db
from models.api_keys import ApiKey

security = HTTPBearer()


def require_token(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db),
) -> dict:
    """
    Dependency to enforce API token authentication against DB.
    Returns a dict with authentication details.
    Raises 401 if token is invalid or missing.
    Also sets Postgres session variable for RLS policies.
    """
    token = credentials.credentials

    # Look up API key
    api_key = db.query(ApiKey).filter(ApiKey.token == token).first()
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Set token in session for Postgres RLS
    db.execute(text("SET app.current_token = :token"), {"token": token})

    return {
        "user_authenticated": True,
        "role": api_key.role,
        "is_admin": api_key.is_admin,
        "has_token": True if api_key.token else False,
        "expires_at": api_key.expires_at
    }


def is_authenticated(request: Request) -> dict:
    """
    Returns dict with user_authenticated flag, role, and username if token is valid.
    Lightweight — no Depends(), just a direct DB check.
    """
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1]

        with get_db() as db:
            api_key = db.query(ApiKey).filter(ApiKey.token == token).first()
            if api_key:
                return {
                    "user_authenticated": True,
                    "username": api_key.description or "service",
                    "role": api_key.role,
                    "expires_at": api_key.expires_at,
                }

    return {"user_authenticated": False}
