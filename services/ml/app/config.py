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
    service_name: str = "ml-service"
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"

    # ML Models
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dimension: int = 384
    topic_model: str = "facebook/bart-large-mnli"
    similarity_threshold: float = 0.7

    # Portfolio ingestion
    max_scrape_retries: int = 3
    scrape_timeout_seconds: int = 30
    max_portfolio_items_per_freelancer: int = 100

    # Trust score
    trust_score_smoothing_factor: float = 0.3

    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:8080"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
