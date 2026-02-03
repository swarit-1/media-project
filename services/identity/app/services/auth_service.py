from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

import sys
sys.path.insert(0, "/app")
from shared.auth import (
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
)
from shared.errors import AuthenticationError

from ..models import User
from ..models.user import UserStatus
from ..schemas import LoginRequest, TokenResponse
from .user_service import UserService


class AuthService:
    """Service for authentication operations."""

    def __init__(self):
        self.user_service = UserService()

    async def authenticate(
        self,
        db: AsyncSession,
        data: LoginRequest,
    ) -> TokenResponse:
        """Authenticate a user and return tokens."""
        user = await self.user_service.get_user_by_email(db, data.email)

        if not user or not user.password_hash:
            raise AuthenticationError("Invalid email or password")

        if not verify_password(data.password, user.password_hash):
            raise AuthenticationError("Invalid email or password")

        if user.status != UserStatus.ACTIVE:
            raise AuthenticationError("Account is not active")

        # Update last login
        await self.user_service.update_last_login(db, user.id)

        # Generate tokens
        return self._create_tokens(user)

    async def refresh_tokens(
        self,
        db: AsyncSession,
        refresh_token: str,
    ) -> TokenResponse:
        """Refresh access token using refresh token."""
        payload = verify_token(refresh_token, expected_type="refresh")
        if not payload:
            raise AuthenticationError("Invalid refresh token")

        user = await self.user_service.get_user_by_id(db, UUID(payload.sub))
        if not user:
            raise AuthenticationError("User not found")

        if user.status != UserStatus.ACTIVE:
            raise AuthenticationError("Account is not active")

        return self._create_tokens(user)

    def _create_tokens(self, user: User) -> TokenResponse:
        """Create access and refresh tokens for a user."""
        # Get newsroom IDs if editor
        newsroom_ids: list[str] = []
        permissions: list[str] = []

        access_token = create_access_token(
            user_id=user.id,
            email=user.email,
            role=user.role.value,
            newsrooms=newsroom_ids,
            permissions=permissions,
        )
        refresh_token = create_refresh_token(user_id=user.id)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=15 * 60,  # 15 minutes in seconds
        )

    async def get_current_user(
        self,
        db: AsyncSession,
        token: str,
    ) -> Optional[User]:
        """Get the current user from an access token."""
        payload = verify_token(token, expected_type="access")
        if not payload:
            return None

        return await self.user_service.get_user_by_id(db, UUID(payload.sub))
