import math
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

import sys
sys.path.insert(0, "/app")
from shared.db import get_db

from ..models.squad import SquadInstanceStatus
from ..schemas.squad import (
    SquadTemplateCreate,
    SquadTemplateUpdate,
    SquadTemplateResponse,
    SquadInstanceCreate,
    SquadInstanceResponse,
    SquadMemberInvite,
    SquadMemberResponse,
    SquadMemberAction,
)
from ..services.squad_service import SquadService
from .deps import require_editor, require_freelancer, require_newsroom_id, get_current_user_role

router = APIRouter()
squad_service = SquadService()


# --- Template Endpoints ---

@router.post("/templates", response_model=SquadTemplateResponse, status_code=201)
async def create_template(
    data: SquadTemplateCreate,
    editor_id: UUID = Depends(require_editor),
    newsroom_id: UUID = Depends(require_newsroom_id),
    db: AsyncSession = Depends(get_db),
):
    """Create a squad template. Requires editor role."""
    template = await squad_service.create_template(db, data, newsroom_id, editor_id)
    await db.commit()
    return template


@router.get("/templates", response_model=dict)
async def list_templates(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    editor_id: UUID = Depends(require_editor),
    newsroom_id: UUID = Depends(require_newsroom_id),
    db: AsyncSession = Depends(get_db),
):
    """List squad templates for a newsroom."""
    templates, total = await squad_service.list_templates(
        db, newsroom_id, page=page, per_page=per_page,
    )
    return {
        "results": [SquadTemplateResponse.model_validate(t) for t in templates],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total_results": total,
            "total_pages": math.ceil(total / per_page) if total > 0 else 0,
        },
    }


@router.get("/templates/{template_id}", response_model=SquadTemplateResponse)
async def get_template(
    template_id: UUID,
    editor_id: UUID = Depends(require_editor),
    db: AsyncSession = Depends(get_db),
):
    """Get a squad template by ID."""
    template = await squad_service.get_template_by_id(db, template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Squad template not found"},
        )
    return template


@router.patch("/templates/{template_id}", response_model=SquadTemplateResponse)
async def update_template(
    template_id: UUID,
    data: SquadTemplateUpdate,
    editor_id: UUID = Depends(require_editor),
    newsroom_id: UUID = Depends(require_newsroom_id),
    db: AsyncSession = Depends(get_db),
):
    """Update a squad template."""
    template = await squad_service.get_template_by_id(db, template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Squad template not found"},
        )
    if template.newsroom_id != newsroom_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "NOT_OWNER", "message": "Template belongs to another newsroom"},
        )
    updated = await squad_service.update_template(db, template, data)
    await db.commit()
    return updated


@router.delete("/templates/{template_id}", status_code=204)
async def delete_template(
    template_id: UUID,
    editor_id: UUID = Depends(require_editor),
    newsroom_id: UUID = Depends(require_newsroom_id),
    db: AsyncSession = Depends(get_db),
):
    """Delete a squad template."""
    template = await squad_service.get_template_by_id(db, template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Squad template not found"},
        )
    if template.newsroom_id != newsroom_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "NOT_OWNER", "message": "Template belongs to another newsroom"},
        )
    await squad_service.delete_template(db, template)
    await db.commit()


# --- Instance Endpoints ---

@router.post("/instances", response_model=SquadInstanceResponse, status_code=201)
async def create_instance(
    data: SquadInstanceCreate,
    editor_id: UUID = Depends(require_editor),
    newsroom_id: UUID = Depends(require_newsroom_id),
    db: AsyncSession = Depends(get_db),
):
    """Create a squad instance from a template."""
    template = await squad_service.get_template_by_id(db, data.template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Squad template not found"},
        )
    if template.newsroom_id != newsroom_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "NOT_OWNER", "message": "Template belongs to another newsroom"},
        )

    instance = await squad_service.create_instance(db, data, template, editor_id)
    await db.commit()
    # Re-fetch with members loaded
    instance = await squad_service.get_instance_by_id(db, instance.id)
    return instance


@router.get("/instances", response_model=dict)
async def list_instances(
    status_filter: Optional[str] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    editor_id: UUID = Depends(require_editor),
    newsroom_id: UUID = Depends(require_newsroom_id),
    db: AsyncSession = Depends(get_db),
):
    """List squad instances for a newsroom."""
    s_status = None
    if status_filter:
        try:
            s_status = SquadInstanceStatus(status_filter)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "INVALID_STATUS", "message": f"Invalid status: {status_filter}"},
            )

    instances, total = await squad_service.list_instances(
        db, newsroom_id, status=s_status, page=page, per_page=per_page,
    )
    return {
        "results": [SquadInstanceResponse.model_validate(i) for i in instances],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total_results": total,
            "total_pages": math.ceil(total / per_page) if total > 0 else 0,
        },
    }


@router.get("/instances/{instance_id}", response_model=SquadInstanceResponse)
async def get_instance(
    instance_id: UUID,
    user_info: tuple[UUID, str] = Depends(get_current_user_role),
    db: AsyncSession = Depends(get_db),
):
    """Get a squad instance by ID with members."""
    instance = await squad_service.get_instance_by_id(db, instance_id)
    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Squad instance not found"},
        )
    return instance


@router.post("/instances/{instance_id}/activate", response_model=SquadInstanceResponse)
async def activate_instance(
    instance_id: UUID,
    editor_id: UUID = Depends(require_editor),
    newsroom_id: UUID = Depends(require_newsroom_id),
    db: AsyncSession = Depends(get_db),
):
    """Activate a squad (all minimum slots filled)."""
    instance = await squad_service.get_instance_by_id(db, instance_id)
    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Squad instance not found"},
        )
    if instance.newsroom_id != newsroom_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "NOT_OWNER", "message": "Squad belongs to another newsroom"},
        )

    try:
        instance = await squad_service.activate_instance(db, instance)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_STATE", "message": str(e)},
        )

    await db.commit()
    return instance


@router.post("/instances/{instance_id}/complete", response_model=SquadInstanceResponse)
async def complete_instance(
    instance_id: UUID,
    editor_id: UUID = Depends(require_editor),
    newsroom_id: UUID = Depends(require_newsroom_id),
    db: AsyncSession = Depends(get_db),
):
    """Mark a squad as completed."""
    instance = await squad_service.get_instance_by_id(db, instance_id)
    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Squad instance not found"},
        )
    if instance.newsroom_id != newsroom_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "NOT_OWNER", "message": "Squad belongs to another newsroom"},
        )

    try:
        instance = await squad_service.complete_instance(db, instance)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_STATE", "message": str(e)},
        )

    await db.commit()
    return instance


@router.post("/instances/{instance_id}/disband", response_model=SquadInstanceResponse)
async def disband_instance(
    instance_id: UUID,
    editor_id: UUID = Depends(require_editor),
    newsroom_id: UUID = Depends(require_newsroom_id),
    db: AsyncSession = Depends(get_db),
):
    """Disband a squad."""
    instance = await squad_service.get_instance_by_id(db, instance_id)
    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Squad instance not found"},
        )
    if instance.newsroom_id != newsroom_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "NOT_OWNER", "message": "Squad belongs to another newsroom"},
        )

    try:
        instance = await squad_service.disband_instance(db, instance)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_STATE", "message": str(e)},
        )

    await db.commit()
    return instance


# --- Member Endpoints ---

@router.post(
    "/instances/{instance_id}/members",
    response_model=SquadMemberResponse,
    status_code=201,
)
async def invite_member(
    instance_id: UUID,
    data: SquadMemberInvite,
    editor_id: UUID = Depends(require_editor),
    newsroom_id: UUID = Depends(require_newsroom_id),
    db: AsyncSession = Depends(get_db),
):
    """Invite a freelancer to a squad."""
    instance = await squad_service.get_instance_by_id(db, instance_id)
    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Squad instance not found"},
        )
    if instance.newsroom_id != newsroom_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "NOT_OWNER", "message": "Squad belongs to another newsroom"},
        )

    try:
        member = await squad_service.invite_member(db, instance, data, editor_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_STATE", "message": str(e)},
        )

    await db.commit()
    return member


@router.get("/invitations/my", response_model=list[SquadMemberResponse])
async def list_my_invitations(
    freelancer_id: UUID = Depends(require_freelancer),
    db: AsyncSession = Depends(get_db),
):
    """List squad invitations for the current freelancer."""
    members = await squad_service.get_freelancer_invitations(db, freelancer_id)
    return [SquadMemberResponse.model_validate(m) for m in members]


@router.post(
    "/members/{member_id}/respond",
    response_model=SquadMemberResponse,
)
async def respond_to_invitation(
    member_id: UUID,
    data: SquadMemberAction,
    freelancer_id: UUID = Depends(require_freelancer),
    db: AsyncSession = Depends(get_db),
):
    """Accept or decline a squad invitation."""
    member = await squad_service.get_member_by_id(db, member_id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Squad member record not found"},
        )
    if member.freelancer_id != freelancer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "NOT_OWNER", "message": "This invitation is not for you"},
        )

    try:
        member = await squad_service.respond_to_invitation(db, member, data.action)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_STATE", "message": str(e)},
        )

    await db.commit()
    return member


@router.delete(
    "/instances/{instance_id}/members/{member_id}",
    response_model=SquadMemberResponse,
)
async def remove_member(
    instance_id: UUID,
    member_id: UUID,
    editor_id: UUID = Depends(require_editor),
    newsroom_id: UUID = Depends(require_newsroom_id),
    db: AsyncSession = Depends(get_db),
):
    """Remove a member from a squad."""
    instance = await squad_service.get_instance_by_id(db, instance_id)
    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Squad instance not found"},
        )
    if instance.newsroom_id != newsroom_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "NOT_OWNER", "message": "Squad belongs to another newsroom"},
        )

    member = await squad_service.get_member_by_id(db, member_id)
    if not member or member.squad_id != instance_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Squad member not found in this squad"},
        )

    member = await squad_service.remove_member(db, member)
    await db.commit()
    return member
