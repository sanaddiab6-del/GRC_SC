"""
Secrets Management with Azure Key Vault
Production-grade secrets handling with fallback support
Compliant with: NCA ECC-IS-7, PDPL Article 25, ISO 27001 A.8.24
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Optional

from pydantic import BaseModel, Field


# ============================================================================
# Secrets Provider Interface
# ============================================================================

class SecretsProvider:
    """Abstract interface for secrets providers"""
    
    def get_secret(self, secret_name: str) -> str:
        """Get secret value by name"""
        raise NotImplementedError
    
    def set_secret(self, secret_name: str, secret_value: str) -> None:
        """Set secret value (if supported)"""
        raise NotImplementedError
    
    def delete_secret(self, secret_name: str) -> None:
        """Delete secret (if supported)"""
        raise NotImplementedError
    
    def list_secrets(self) -> list[str]:
        """List all secret names"""
        raise NotImplementedError


# ============================================================================
# Environment Variables Provider (Development)
# ============================================================================

class EnvironmentSecretsProvider(SecretsProvider):
    """
    Load secrets from environment variables
    Fallback for local development
    """
    
    def get_secret(self, secret_name: str) -> str:
        """Get secret from environment variable"""
        value = os.getenv(secret_name)
        if value is None:
            raise ValueError(
                f"Secret '{secret_name}' not found in environment variables. "
                f"Set {secret_name}=<value> or use Azure Key Vault."
            )
        return value
    
    def set_secret(self, secret_name: str, secret_value: str) -> None:
        """Not supported for environment variables"""
        raise NotImplementedError("Cannot set environment variables at runtime")
    
    def delete_secret(self, secret_name: str) -> None:
        """Not supported for environment variables"""
        raise NotImplementedError("Cannot delete environment variables at runtime")
    
    def list_secrets(self) -> list[str]:
        """List environment variables (limited)"""
        return list(os.environ.keys())


# ============================================================================
# Azure Key Vault Provider (Production)
# ============================================================================

class AzureKeyVaultProvider(SecretsProvider):
    """
    Load secrets from Azure Key Vault
    Production-ready secrets management
    
    Requires:
        - azure-identity
        - azure-keyvault-secrets
    
    Environment Variables:
        - AZURE_KEY_VAULT_NAME: Name of the Key Vault
        - AZURE_TENANT_ID: Azure AD tenant ID
        - AZURE_CLIENT_ID: Service principal client ID
        - AZURE_CLIENT_SECRET: Service principal secret
    """
    
    def __init__(
        self,
        vault_name: Optional[str] = None,
        tenant_id: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
    ):
        """
        Initialize Azure Key Vault client
        
        Args:
            vault_name: Key Vault name (or from AZURE_KEY_VAULT_NAME)
            tenant_id: Azure AD tenant ID (or from AZURE_TENANT_ID)
            client_id: Service principal client ID (or from AZURE_CLIENT_ID)
            client_secret: Service principal secret (or from AZURE_CLIENT_SECRET)
        """
        try:
            from azure.identity import ClientSecretCredential
            from azure.keyvault.secrets import SecretClient
        except ImportError:
            raise ImportError(
                "Azure Key Vault dependencies not installed. "
                "Run: pip install azure-identity azure-keyvault-secrets"
            )
        
        # Get configuration from environment or parameters
        self.vault_name = vault_name or os.getenv("AZURE_KEY_VAULT_NAME")
        tenant_id = tenant_id or os.getenv("AZURE_TENANT_ID")
        client_id = client_id or os.getenv("AZURE_CLIENT_ID")
        client_secret = client_secret or os.getenv("AZURE_CLIENT_SECRET")
        
        if not all([self.vault_name, tenant_id, client_id, client_secret]):
            raise ValueError(
                "Azure Key Vault configuration incomplete. Required: "
                "AZURE_KEY_VAULT_NAME, AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET"
            )
        
        # Build vault URL
        self.vault_url = f"https://{self.vault_name}.vault.azure.net"
        
        # Create credential
        self.credential = ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret,
        )
        
        # Create secret client
        self.client = SecretClient(
            vault_url=self.vault_url,
            credential=self.credential,
        )
    
    def get_secret(self, secret_name: str) -> str:
        """
        Get secret from Azure Key Vault
        
        Args:
            secret_name: Name of the secret
        
        Returns:
            Secret value
        """
        try:
            secret = self.client.get_secret(secret_name)
            return secret.value
        except Exception as e:
            raise ValueError(
                f"Failed to retrieve secret '{secret_name}' from Azure Key Vault: {str(e)}"
            )
    
    def set_secret(self, secret_name: str, secret_value: str) -> None:
        """
        Set secret in Azure Key Vault
        
        Args:
            secret_name: Name of the secret
            secret_value: Secret value
        """
        try:
            self.client.set_secret(secret_name, secret_value)
        except Exception as e:
            raise ValueError(
                f"Failed to set secret '{secret_name}' in Azure Key Vault: {str(e)}"
            )
    
    def delete_secret(self, secret_name: str) -> None:
        """
        Delete secret from Azure Key Vault
        
        Args:
            secret_name: Name of the secret
        """
        try:
            poller = self.client.begin_delete_secret(secret_name)
            poller.wait()
        except Exception as e:
            raise ValueError(
                f"Failed to delete secret '{secret_name}' from Azure Key Vault: {str(e)}"
            )
    
    def list_secrets(self) -> list[str]:
        """
        List all secret names in Azure Key Vault
        
        Returns:
            List of secret names
        """
        try:
            return [secret.name for secret in self.client.list_properties_of_secrets()]
        except Exception as e:
            raise ValueError(
                f"Failed to list secrets from Azure Key Vault: {str(e)}"
            )


# ============================================================================
# Secrets Manager (Singleton)
# ============================================================================

class SecretsManager:
    """
    Centralized secrets management
    Automatically selects provider based on environment
    """
    
    _instance: Optional[SecretsManager] = None
    
    def __init__(self, provider: Optional[SecretsProvider] = None):
        """
        Initialize secrets manager
        
        Args:
            provider: Secrets provider (auto-detected if None)
        """
        if provider is None:
            provider = self._auto_detect_provider()
        
        self.provider = provider
        self._cache: dict[str, str] = {}
    
    @classmethod
    def get_instance(cls) -> SecretsManager:
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @staticmethod
    def _auto_detect_provider() -> SecretsProvider:
        """
        Auto-detect secrets provider based on environment
        
        Returns:
            SecretsProvider instance
        """
        # Check if Azure Key Vault is configured
        if os.getenv("AZURE_KEY_VAULT_NAME"):
            try:
                return AzureKeyVaultProvider()
            except Exception as e:
                print(f"⚠️  Failed to initialize Azure Key Vault: {e}")
                print("⚠️  Falling back to environment variables")
        
        # Fallback to environment variables
        return EnvironmentSecretsProvider()
    
    def get_secret(self, secret_name: str, use_cache: bool = True) -> str:
        """
        Get secret value
        
        Args:
            secret_name: Name of the secret
            use_cache: Use cached value if available
        
        Returns:
            Secret value
        """
        if use_cache and secret_name in self._cache:
            return self._cache[secret_name]
        
        value = self.provider.get_secret(secret_name)
        
        if use_cache:
            self._cache[secret_name] = value
        
        return value
    
    def set_secret(self, secret_name: str, secret_value: str) -> None:
        """
        Set secret value
        
        Args:
            secret_name: Name of the secret
            secret_value: Secret value
        """
        self.provider.set_secret(secret_name, secret_value)
        
        # Invalidate cache
        if secret_name in self._cache:
            del self._cache[secret_name]
    
    def delete_secret(self, secret_name: str) -> None:
        """
        Delete secret
        
        Args:
            secret_name: Name of the secret
        """
        self.provider.delete_secret(secret_name)
        
        # Invalidate cache
        if secret_name in self._cache:
            del self._cache[secret_name]
    
    def list_secrets(self) -> list[str]:
        """List all secret names"""
        return self.provider.list_secrets()
    
    def clear_cache(self) -> None:
        """Clear secrets cache"""
        self._cache.clear()


# ============================================================================
# Convenience Functions
# ============================================================================

@lru_cache(maxsize=1)
def get_secrets_manager() -> SecretsManager:
    """Get secrets manager singleton (cached)"""
    return SecretsManager.get_instance()


def get_secret(secret_name: str) -> str:
    """
    Get secret value (convenience function)
    
    Args:
        secret_name: Name of the secret
    
    Returns:
        Secret value
    """
    manager = get_secrets_manager()
    return manager.get_secret(secret_name)


# ============================================================================
# Application Secrets Configuration
# ============================================================================

class AppSecrets(BaseModel):
    """
    Application secrets configuration
    All secrets loaded from Key Vault or environment
    """
    
    # JWT Secrets
    jwt_secret_key: str = Field(
        default_factory=lambda: get_secret("JWT-SECRET-KEY")
    )
    jwt_algorithm: str = Field(default="HS256")
    jwt_access_token_expire_minutes: int = Field(default=30)
    jwt_refresh_token_expire_days: int = Field(default=7)
    
    # Database Secrets
    database_url: str = Field(
        default_factory=lambda: get_secret("DATABASE-URL")
    )
    database_password: str = Field(
        default_factory=lambda: get_secret("DATABASE-PASSWORD")
    )
    
    # Redis Secrets
    redis_url: str = Field(
        default_factory=lambda: get_secret("REDIS-URL")
    )
    redis_password: Optional[str] = Field(
        default_factory=lambda: get_secret("REDIS-PASSWORD") if os.getenv("REDIS-PASSWORD") else None
    )
    
    # Azure Secrets
    azure_tenant_id: str = Field(
        default_factory=lambda: get_secret("AZURE-TENANT-ID")
    )
    azure_client_id: str = Field(
        default_factory=lambda: get_secret("AZURE-CLIENT-ID")
    )
    azure_client_secret: str = Field(
        default_factory=lambda: get_secret("AZURE-CLIENT-SECRET")
    )
    
    # API Keys
    openai_api_key: Optional[str] = Field(
        default_factory=lambda: get_secret("OPENAI-API-KEY") if os.getenv("OPENAI-API-KEY") else None
    )
    
    # Encryption Keys
    data_encryption_key: str = Field(
        default_factory=lambda: get_secret("DATA-ENCRYPTION-KEY")
    )
    
    class Config:
        """Pydantic configuration"""
        env_file = ".env"
        case_sensitive = False


@lru_cache(maxsize=1)
def get_app_secrets() -> AppSecrets:
    """Get application secrets (cached)"""
    return AppSecrets()


# ============================================================================
# Example Usage
# ============================================================================

"""
# Setup Azure Key Vault (Production):

export AZURE_KEY_VAULT_NAME="sanadcom-kv"
export AZURE_TENANT_ID="your-tenant-id"
export AZURE_CLIENT_ID="your-client-id"
export AZURE_CLIENT_SECRET="your-client-secret"

# Add secrets to Key Vault:
az keyvault secret set --vault-name sanadcom-kv --name JWT-SECRET-KEY --value "your-secret-key"
az keyvault secret set --vault-name sanadcom-kv --name DATABASE-URL --value "postgresql://..."

# Use in application:

from src.backend.core.secrets import get_secret, get_app_secrets

# Get individual secret
jwt_key = get_secret("JWT-SECRET-KEY")

# Get all secrets
secrets = get_app_secrets()
print(secrets.jwt_secret_key)
print(secrets.database_url)

# Manual secrets management:

from src.backend.core.secrets import get_secrets_manager

manager = get_secrets_manager()

# Set secret
manager.set_secret("NEW-SECRET", "secret-value")

# List secrets
all_secrets = manager.list_secrets()

# Delete secret
manager.delete_secret("OLD-SECRET")

# Development (Without Azure Key Vault):

export JWT-SECRET-KEY="dev-secret-key"
export DATABASE-URL="postgresql://localhost/sanadcom"

# Application will automatically fallback to environment variables
"""
