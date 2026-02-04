from fastapi import APIRouter

from .search import router as search_router
from .squads import router as squads_router

api_router = APIRouter()

api_router.include_router(search_router, prefix="/discovery", tags=["Discovery"])
api_router.include_router(squads_router, prefix="/squads", tags=["Squad Builder"])
