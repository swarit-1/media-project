from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

import sys
sys.path.insert(0, "/app")
from shared.db import get_db
from shared.errors import NotFoundError

from ..schemas import (
    SearchRequest,
    SearchResponse,
    FreelancerDetailResponse,
)
from ..services import SearchService

router = APIRouter()


@router.post("/search", response_model=SearchResponse)
async def search_freelancers(
    request: SearchRequest,
    db: AsyncSession = Depends(get_db),
) -> SearchResponse:
    """
    Search for freelancers with filtering and sorting.

    Supports filtering by:
    - Beats (topics/expertise areas)
    - Location (state, country)
    - Availability status
    - Minimum trust score
    - Rate range

    Returns paginated results with facets for UI filtering.
    """
    search_service = SearchService()
    return await search_service.search(db, request)


@router.get("/freelancers/{freelancer_id}", response_model=FreelancerDetailResponse)
async def get_freelancer_detail(
    freelancer_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> FreelancerDetailResponse:
    """
    Get full freelancer profile details.

    Returns complete profile information including:
    - Basic profile information
    - Rates and availability
    - Verification status
    - Trust scores
    - Portfolio highlights (when available)
    """
    search_service = SearchService()
    try:
        return await search_service.get_freelancer_detail(db, freelancer_id)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": e.code, "message": e.message, "details": e.details},
        )
