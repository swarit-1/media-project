from fastapi import APIRouter

from .payments import router as payments_router
from .webhooks import router as webhooks_router
from .compliance import router as compliance_router
from .ledger import router as ledger_router

api_router = APIRouter()

api_router.include_router(payments_router, prefix="/payments", tags=["Payments"])
api_router.include_router(webhooks_router, prefix="/webhooks", tags=["Webhooks"])
api_router.include_router(compliance_router, prefix="/compliance", tags=["Compliance"])
api_router.include_router(ledger_router, prefix="/ledger", tags=["Vendor Ledger"])
