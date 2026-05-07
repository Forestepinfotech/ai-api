"""
Configuration module for AI Reception System
Handles environment variables and Supabase connection
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # Supabase
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_anon_key: str = os.getenv("SUPABASE_ANON_KEY", "")
    supabase_service_role_key: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    
    # API
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", 8000))
    environment: str = os.getenv("ENVIRONMENT", "development")
    
    # AI/ML
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    model_name: str = os.getenv("MODEL_NAME", "claude-haiku-4-5")
    temperature: float = float(os.getenv("TEMPERATURE", 0.7))
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "")
    
    # JWT
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    
    # Feature flags
    swagger_enabled: bool = os.getenv("SWAGGER_ENABLED", "true").lower() == "true"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

# Initialize settings
settings = get_settings()
