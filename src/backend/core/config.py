"""
Core configuration management using Pydantic settings
Supports environment variables and .env file
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Union
from pydantic import field_validator


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application
    APP_NAME: str = "SICO GRC Platform"
    DEBUG: bool = False
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: Union[List[str], str] = "http://localhost:3000,http://localhost:8000"
    
    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
      # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./sico_grc.db"  # Async for application
    DATABASE_URL_SYNC: str = "sqlite:///./sico_grc.db"  # Synchronous for direct SQL scripts
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
    
    # Security (NCA ECC-IS-3, PDPL Article 29)
    SECRET_KEY: str = ""  # REQUIRED: Must be set via environment variable (min 32 chars)
    ENCRYPTION_KEY: str = ""  # Fernet key for field-level encryption, from Azure Key Vault
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return not self.DEBUG and "localhost" not in self.DATABASE_URL
    
    # Azure Key Vault (for production)
    AZURE_KEY_VAULT_URL: str = ""
    AZURE_CLIENT_ID: str = ""
    AZURE_CLIENT_SECRET: str = ""
    AZURE_TENANT_ID: str = ""
    
    # Rate Limiting (NCA ECC-IS-3)
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # TLS/HTTPS
    TLS_ENABLED: bool = True
    TLS_CERT_PATH: str = "/etc/ssl/certs/server.crt"
    TLS_KEY_PATH: str = "/etc/ssl/private/server.key"
    
    # Audit Logging (NCA ECC-IS-5, 7-year retention)
    AUDIT_LOG_RETENTION_YEARS: int = 7
    AUDIT_LOG_STORAGE_PATH: str = "/var/log/sico/audit"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow"
    )


settings = Settings()

# Security validation on startup
if len(settings.SECRET_KEY) < 32:
    raise ValueError(
        "CRITICAL SECURITY ERROR: SECRET_KEY must be at least 32 characters. "
        "Generate a secure key using: openssl rand -hex 32"
    )

if settings.is_production and settings.SECRET_KEY == "your-secret-key-change-in-production":
    raise ValueError(
        "CRITICAL SECURITY ERROR: Default SECRET_KEY detected in production. "
        "Set a unique SECRET_KEY environment variable."
    )

if settings.is_production and not settings.TLS_ENABLED:
    raise ValueError(
        "NCA ECC COMPLIANCE ERROR: TLS/HTTPS must be enabled in production (NCA ECC-IS-3)"
    )

if settings.is_production and not settings.ENCRYPTION_KEY:
    raise ValueError(
        "PDPL COMPLIANCE ERROR: ENCRYPTION_KEY must be set for PII encryption (PDPL Article 29)"
    )
