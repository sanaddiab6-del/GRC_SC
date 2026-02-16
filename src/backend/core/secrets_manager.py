"""
Production-Grade Secrets Management
Supports Azure Key Vault, environment variables, and local development
Complies with NCA ECC-IS-3 and PDPL Article 29
"""

import os
import logging
from typing import Optional
from cryptography.fernet import Fernet
import base64
import hashlib

logger = logging.getLogger(__name__)


class SecretsManager:
    """
    Centralized secrets management for SICO GRC Platform
    Supports multiple backends: Azure Key Vault, environment variables, local
    """
    
    def __init__(self):
        self.is_production = os.getenv("ENV", "development") == "production"
        self._azure_client = None
        self._fernet = None
        self._init_encryption()
    
    def _init_encryption(self):
        """Initialize encryption engine for field-level encryption"""
        encryption_key = os.getenv("ENCRYPTION_KEY")
        
        if encryption_key:
            try:
                self._fernet = Fernet(encryption_key.encode())
                logger.info("✓ Field-level encryption initialized")
            except Exception as e:
                logger.error(f"Failed to initialize encryption: {e}")
                if self.is_production:
                    raise ValueError("ENCRYPTION_KEY is invalid in production")
        else:
            logger.warning("⚠️ ENCRYPTION_KEY not set - field-level encryption disabled")
            if self.is_production:
                raise ValueError("ENCRYPTION_KEY required in production (PDPL Article 29)")
    
    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Retrieve secret with fallback chain:
        1. Azure Key Vault (production)
        2. Environment variable
        3. Default value
        """
        # Try Azure Key Vault in production
        if self.is_production and self._azure_client:
            try:
                secret = self._get_from_azure(key)
                if secret:
                    return secret
            except Exception as e:
                logger.warning(f"Azure Key Vault failed for {key}: {e}")
        
        # Fallback to environment variable
        value = os.getenv(key, default)
        if value is None:
            logger.warning(f"Secret '{key}' not found")
        return value
    
    def _get_from_azure(self, key: str) -> Optional[str]:
        """Retrieve secret from Azure Key Vault"""
        if not self._azure_client:
            self._init_azure_client()
        
        if self._azure_client:
            try:
                secret = self._azure_client.get_secret(key)
                return secret.value
            except Exception as e:
                logger.error(f"Failed to retrieve {key} from Azure: {e}")
        return None
    
    def _init_azure_client(self):
        """Initialize Azure Key Vault client"""
        try:
            from azure.identity import DefaultAzureCredential  # type: ignore
            from azure.keyvault.secrets import SecretClient  # type: ignore
            
            vault_url = os.getenv("AZURE_KEY_VAULT_URL")
            if vault_url:
                credential = DefaultAzureCredential()
                self._azure_client = SecretClient(vault_url=vault_url, credential=credential)
                logger.info("✓ Azure Key Vault client initialized")
        except ImportError:
            logger.warning("Azure SDK not installed - using environment variables only")
        except Exception as e:
            logger.error(f"Failed to initialize Azure client: {e}")
    
    def encrypt_field(self, data: str) -> str:
        """
        Encrypt sensitive field (PII, credentials)
        Required for PDPL Article 29 compliance
        """
        if not self._fernet:
            raise ValueError("Encryption not initialized - set ENCRYPTION_KEY")
        
        try:
            encrypted = self._fernet.encrypt(data.encode())
            return base64.b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise
    
    def decrypt_field(self, encrypted_data: str) -> str:
        """Decrypt sensitive field"""
        if not self._fernet:
            raise ValueError("Encryption not initialized - set ENCRYPTION_KEY")
        
        try:
            decoded = base64.b64decode(encrypted_data.encode())
            decrypted = self._fernet.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt (NCA ECC-IS-3)"""
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.verify(plain_password, hashed_password)
    
    def generate_encryption_key(self) -> str:
        """Generate a new Fernet encryption key"""
        return Fernet.generate_key().decode()
    
    def generate_secret_key(self, length: int = 32) -> str:
        """Generate a secure random secret key"""
        import secrets
        return secrets.token_urlsafe(length)


# Global secrets manager instance
secrets_manager = SecretsManager()


def get_secrets_manager() -> SecretsManager:
    """Dependency injection for FastAPI"""
    return secrets_manager
