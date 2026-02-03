from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

import sys
sys.path.insert(0, "/app")
from shared.auth import verify_token

security = HTTPBearer()


async def get_current_user_role(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> tuple[UUID, str]:
    """Dependency to get the current user ID and role from token."""
    token = credentials.credentials
    payload = verify_token(token, expected_type="access")

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_TOKEN", "message": "Invalid or expired token"},
        )

    return UUID(payload.sub), payload.role


async def require_freelancer(
    user_info: tuple[UUID, str] = Depends(get_current_user_role),
) -> UUID:
    """Dependency to require freelancer role. Returns user ID."""
    user_id, role = user_info
    if role != "freelancer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "NOT_FREELANCER", "message": "Requires freelancer account"},
        )
    return user_id


async def require_editor(
    user_info: tuple[UUID, str] = Depends(get_current_user_role),
) -> UUID:
    """Dependency to require editor role. Returns user ID."""
    user_id, role = user_info
    if role != "editor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "NOT_EDITOR", "message": "Requires editor account"},
        )
    return user_id


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> UUID:
    """Get the current user ID from token."""
    token = credentials.credentials
    payload = verify_token(token, expected_type="access")

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_TOKEN", "message": "Invalid or expired token"},
        )

    return UUID(payload.sub)
