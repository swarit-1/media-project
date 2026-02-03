from typing import Optional
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

import sys
sys.path.insert(0, "/app")
from shared.db import get_db
from shared.auth import verify_token
from shared.errors import AuthenticationError, AuthorizationError

from ..models import User
from ..models.user import UserRole
from ..services import UserService

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Dependency to get the current authenticated user."""
    token = credentials.credentials
    payload = verify_token(token, expected_type="access")

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_TOKEN", "message": "Invalid or expired token"},
        )

    user_service = UserService()
    user = await user_service.get_user_by_id(db, UUID(payload.sub))

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "USER_NOT_FOUND", "message": "User not found"},
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Dependency to get the current active user."""
    if current_user.status.value != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "ACCOUNT_INACTIVE", "message": "Account is not active"},
        )
    return current_user


async def get_current_freelancer(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Dependency to get a freelancer user."""
    if current_user.role != UserRole.FREELANCER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "NOT_FREELANCER", "message": "This action requires a freelancer account"},
        )
    return current_user


async def get_current_editor(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Dependency to get an editor user."""
    if current_user.role != UserRole.EDITOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "NOT_EDITOR", "message": "This action requires an editor account"},
        )
    return current_user


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
