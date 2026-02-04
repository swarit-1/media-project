from fastapi import APIRouter

from .pitch_windows import router as windows_router
from .pitches import router as pitches_router
from .assignments import router as assignments_router
from .cms_webhooks import router as cms_webhooks_router

api_router = APIRouter()

api_router.include_router(windows_router, prefix="/pitch-windows", tags=["Pitch Windows"])
api_router.include_router(pitches_router, prefix="/pitches", tags=["Pitches"])
api_router.include_router(assignments_router, prefix="/assignments", tags=["Assignments"])
api_router.include_router(cms_webhooks_router, prefix="/webhooks", tags=["CMS Webhooks"])
