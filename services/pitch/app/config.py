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
    service_name: str = "pitch-service"
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"

    # Pitch limits
    default_pitch_limit_per_week: int = 5
    default_pitch_window_max: int = 50

    # CMS Webhook
    cms_webhook_secret: str = "disabled"

    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:8080"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
