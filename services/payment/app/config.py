from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = "postgresql+asyncpg://newsroom_user:changeme_in_production@localhost:5432/elastic_newsroom"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # JWT (for token validation)
    jwt_secret_key: str = "your-super-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"

    # Service
    service_name: str = "payment-service"
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"

    # Stripe
    stripe_secret_key: str = "sk_test_placeholder"
    stripe_publishable_key: str = "pk_test_placeholder"
    stripe_webhook_secret: str = "whsec_placeholder"

    # Payment settings
    platform_fee_percentage: float = 10.0
    escrow_hold_days: int = 7
    kill_fee_default_percentage: float = 25.0

    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:8080"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
