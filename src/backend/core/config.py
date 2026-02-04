"""
Core configuration management using Pydantic settings
Supports environment variables and .env file
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application
    APP_NAME: str = "SICO GRC Platform"
    DEBUG: bool = False
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/sico_grc"
    DATABASE_ECHO: bool = False
    
    # Vector Database
    VECTOR_DB_TYPE: str = "chroma"  # chroma or weaviate
    VECTOR_DB_HOST: str = "localhost"
    VECTOR_DB_PORT: int = 8001
    
    # Redis Cache
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL: int = 3600  # 1 hour default
    
    # AI/RAG Configuration
    EMBEDDING_MODEL: str = "intfloat/multilingual-e5-large"
    LLM_MODEL: str = "gpt-4"  # or local model
    RAG_CHUNK_SIZE: int = 512
    RAG_CHUNK_OVERLAP: int = 128
    
    # Regulatory Frameworks
    SUPPORTED_FRAMEWORKS: List[str] = ["ECC", "CCC", "PDPL"]
    DEFAULT_LANGUAGE: str = "ar"  # ar or en
    
    # External APIs
    PDPL_API_URL: str = "https://api.dga.gov.sa/pdpl"
    SAMA_API_URL: str = "https://www.sama.gov.sa"
    CITC_API_URL: str = "https://www.citc.gov.sa"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


settings = Settings()
