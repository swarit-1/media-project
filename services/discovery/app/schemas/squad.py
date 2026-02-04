from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# --- Squad Template Schemas ---

class SquadTemplateCreate(BaseModel):
    """Schema for creating a squad template."""

    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    required_beats: list[str] = Field(..., min_length=1)
    required_roles: list[str] = Field(..., min_length=1)
    min_members: int = Field(default=2, ge=1)
    max_members: int = Field(default=10, ge=1, le=50)
    min_trust_score: Optional[float] = Field(None, ge=0, le=1)
    preferred_tiers: Optional[list[str]] = None


class SquadTemplateUpdate(BaseModel):
    """Schema for updating a squad template."""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    required_beats: Optional[list[str]] = None
    required_roles: Optional[list[str]] = None
    min_members: Optional[int] = Field(None, ge=1)
    max_members: Optional[int] = Field(None, ge=1, le=50)
    min_trust_score: Optional[float] = Field(None, ge=0, le=1)
    preferred_tiers: Optional[list[str]] = None


class SquadTemplateResponse(BaseModel):
    """Schema for squad template response."""

    id: UUID
    newsroom_id: UUID
    created_by: UUID
    name: str
    description: Optional[str] = None
    required_beats: list[str]
    required_roles: list[str]
    min_members: int
    max_members: int
    min_trust_score: Optional[float] = None
    preferred_tiers: Optional[list[str]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# --- Squad Instance Schemas ---

class SquadInstanceCreate(BaseModel):
    """Schema for creating a squad instance from a template."""

    template_id: UUID
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    project_brief: Optional[str] = None


class SquadInstanceResponse(BaseModel):
    """Schema for squad instance response."""

    id: UUID
    template_id: UUID
    newsroom_id: UUID
    created_by: UUID
    name: str
    description: Optional[str] = None
    project_brief: Optional[str] = None
    status: str
    members: list["SquadMemberResponse"] = []
    activated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# --- Squad Member Schemas ---

class SquadMemberInvite(BaseModel):
    """Schema for inviting a freelancer to a squad."""

    freelancer_id: UUID
    role: str = Field(..., min_length=1, max_length=100)
    beats: Optional[list[str]] = None
    invitation_message: Optional[str] = None


class SquadMemberResponse(BaseModel):
    """Schema for squad member response."""

    id: UUID
    squad_id: UUID
    freelancer_id: UUID
    role: str
    beats: Optional[list[str]] = None
    status: str
    invited_by: UUID
    invitation_message: Optional[str] = None
    invited_at: datetime
    responded_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SquadMemberAction(BaseModel):
    """Schema for freelancer accepting/declining squad invitation."""

    action: str = Field(..., pattern="^(accept|decline)$")
