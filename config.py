"""
Configuration module for AI Reception System
Handles environment variables and Supabase connection
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings loaded directly from environment variables"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Supabase
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    environment: str = "development"

    # AI/ML
    anthropic_api_key: str = ""
    model_name: str = "claude-haiku-4-5"
    temperature: float = 0.7

    # Database (unused — kept for compatibility)
    database_url: str = ""

    # JWT
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"

    # Vapi.ai
    vapi_api_key: str = ""
    vapi_webhook_secret: str = ""
    default_business_id: str = ""

    # Feature flags
    swagger_enabled: bool = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
