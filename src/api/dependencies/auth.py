from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config import settings

security = HTTPBearer()


def require_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> None:
    """
    Dependency to enforce API token authentication.
    Raises 401 if token is invalid or missing.
    """
    token = credentials.credentials
    if token != settings.API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def is_authenticated(request: Request) -> dict:
    """
    returns dict with user_authenticated flag and username if token is valid.
    """
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1]

        if token == settings.API_TOKEN:
            return {"user_authenticated": True, "username": settings.API_USERNAME}

    return {"user_authenticated": False}
