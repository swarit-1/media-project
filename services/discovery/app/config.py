from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = "postgresql+asyncpg://newsroom_user:changeme_in_production@localhost:5432/elastic_newsroom"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Service
    service_name: str = "discovery-service"
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"

    # Search defaults
    default_page_size: int = 20
    max_page_size: int = 100
    default_search_radius_miles: int = 50

    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:8080"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
