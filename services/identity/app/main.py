from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import sys
sys.path.insert(0, "/app")
from shared.logging import setup_logging, CorrelationIdMiddleware
from shared.errors import register_exception_handlers
from shared.observability import MetricsMiddleware, get_metrics_router

from .config import get_settings
from .api import api_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    setup_logging(settings.service_name)
    yield
    # Shutdown


app = FastAPI(
    title="Identity Service",
    description="User authentication and profile management for Elastic Newsroom Infrastructure",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
)

# Add middlewares
app.add_middleware(MetricsMiddleware, service_name=settings.service_name)
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers
register_exception_handlers(app)

# Include API routes
app.include_router(api_router, prefix="/api/v1")
app.include_router(get_metrics_router(settings.service_name))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "identity"}


@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint."""
    return {"status": "ready", "service": "identity"}
