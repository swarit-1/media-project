from typing import Optional
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
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
            detail={"code": "NOT_FREELANCER", "message": "This action requires a freelancer account"},
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
            detail={"code": "NOT_EDITOR", "message": "This action requires an editor account"},
        )
    return user_id


async def get_newsroom_id(
    x_newsroom_id: Optional[str] = Header(None, alias="X-Newsroom-ID"),
) -> Optional[UUID]:
    """Dependency to get the newsroom ID from header."""
    if not x_newsroom_id:
        return None
    try:
        return UUID(x_newsroom_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_NEWSROOM_ID", "message": "Invalid X-Newsroom-ID header"},
        )


async def require_newsroom_id(
    newsroom_id: Optional[UUID] = Depends(get_newsroom_id),
) -> UUID:
    """Dependency that requires a newsroom ID header."""
    if not newsroom_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "MISSING_NEWSROOM_ID", "message": "X-Newsroom-ID header is required"},
        )
    return newsroom_id
