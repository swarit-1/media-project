import math
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

import sys
sys.path.insert(0, "/app")
from shared.db import get_db

from ..schemas.portfolio import (
    PortfolioIngestRequest,
    PortfolioIngestResponse,
    PortfolioItemResponse,
    PortfolioListResponse,
    PaginationMeta,
)
from ..services.portfolio_service import PortfolioService
from .deps import require_freelancer, get_current_user_id

router = APIRouter()
portfolio_service = PortfolioService()


@router.post("/ingest", response_model=PortfolioIngestResponse)
async def ingest_portfolio_urls(
    data: PortfolioIngestRequest,
    freelancer_id: UUID = Depends(require_freelancer),
    db: AsyncSession = Depends(get_db),
):
    """Ingest portfolio URLs for the current freelancer.

    Scrapes each URL, extracts content, runs NLP analysis,
    and stores as portfolio items.
    """
    queued = 0
    skipped = 0
    errors = []

    for url in data.urls:
        try:
            item = await portfolio_service.ingest_url(
                db, freelancer_id, url
            )
            if item:
                queued += 1
            else:
                errors.append(f"Failed to scrape: {url}")
        except Exception as e:
            errors.append(f"Error processing {url}: {str(e)}")

    return PortfolioIngestResponse(
        queued=queued,
        skipped=skipped,
        errors=errors,
    )


@router.get("/my", response_model=PortfolioListResponse)
async def list_my_portfolio(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    freelancer_id: UUID = Depends(require_freelancer),
    db: AsyncSession = Depends(get_db),
):
    """List portfolio items for the current freelancer."""
    items, total = await portfolio_service.list_freelancer_portfolio(
        db, freelancer_id, page=page, per_page=per_page,
    )

    return PortfolioListResponse(
        results=[PortfolioItemResponse.model_validate(i) for i in items],
        pagination=PaginationMeta(
            page=page,
            per_page=per_page,
            total_results=total,
            total_pages=math.ceil(total / per_page) if total > 0 else 0,
        ),
    )


@router.get("/{item_id}", response_model=PortfolioItemResponse)
async def get_portfolio_item(
    item_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific portfolio item."""
    item = await portfolio_service.get_portfolio_item(db, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Portfolio item not found"},
        )
    return item


@router.get("/freelancer/{freelancer_id}", response_model=PortfolioListResponse)
async def list_freelancer_portfolio(
    freelancer_id: UUID,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List portfolio items for a specific freelancer (public)."""
    items, total = await portfolio_service.list_freelancer_portfolio(
        db, freelancer_id, page=page, per_page=per_page,
    )

    return PortfolioListResponse(
        results=[PortfolioItemResponse.model_validate(i) for i in items],
        pagination=PaginationMeta(
            page=page,
            per_page=per_page,
            total_results=total,
            total_pages=math.ceil(total / per_page) if total > 0 else 0,
        ),
    )
