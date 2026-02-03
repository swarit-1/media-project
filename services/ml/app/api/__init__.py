from fastapi import APIRouter

from .portfolio import router as portfolio_router
from .style import router as style_router
from .duplicate import router as duplicate_router
from .trust_score import router as trust_score_router

api_router = APIRouter()

api_router.include_router(portfolio_router, prefix="/portfolio", tags=["Portfolio"])
api_router.include_router(style_router, prefix="/style", tags=["Style Matching"])
api_router.include_router(duplicate_router, prefix="/duplicate", tags=["Duplicate Detection"])
api_router.include_router(trust_score_router, prefix="/trust-score", tags=["Trust Score"])
