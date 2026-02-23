"""
Tests for Secrets Management System
Coverage: Environment provider, Azure Key Vault, fallback logic
"""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock

from src.backend.core.secrets import (
    EnvironmentSecretsProvider,
    AzureKeyVaultProvider,
    SecretsManager,
    get_secret,
    get_secrets_manager,
)


# ============================================================================
# Test Environment Secrets Provider
# ============================================================================

def test_environment_provider_get_secret():
    """Test getting secret from environment variable"""
    provider = EnvironmentSecretsProvider()
    
    # Set test environment variable
    os.environ["TEST_SECRET"] = "test_value"
    
    value = provider.get_secret("TEST_SECRET")
    assert value == "test_value"
    
    # Cleanup
    del os.environ["TEST_SECRET"]


def test_environment_provider_missing_secret():
    """Test error when secret not in environment"""
    provider = EnvironmentSecretsProvider()
    
    with pytest.raises(ValueError) as exc_info:
        provider.get_secret("NONEXISTENT_SECRET")
    
    assert "not found" in str(exc_info.value).lower()


def test_environment_provider_set_secret_not_supported():
    """Test that setting secrets is not supported"""
    provider = EnvironmentSecretsProvider()
    
    with pytest.raises(NotImplementedError):
        provider.set_secret("TEST", "value")


def test_environment_provider_delete_secret_not_supported():
    """Test that deleting secrets is not supported"""
    provider = EnvironmentSecretsProvider()
    
    with pytest.raises(NotImplementedError):
        provider.delete_secret("TEST")


def test_environment_provider_list_secrets():
    """Test listing environment variables"""
    provider = EnvironmentSecretsProvider()
    
    secrets = provider.list_secrets()
    
    assert isinstance(secrets, list)
    assert len(secrets) > 0  # Should have at least some env vars


# ============================================================================
# Test Azure Key Vault Provider (Mocked)
# ============================================================================

@patch("src.backend.core.secrets.ClientSecretCredential")
@patch("src.backend.core.secrets.SecretClient")
def test_azure_provider_initialization(mock_secret_client, mock_credential):
    """Test Azure Key Vault provider initialization"""
    # Mock Azure SDK
    mock_cred_instance = Mock()
    mock_credential.return_value = mock_cred_instance
    
    mock_client_instance = Mock()
    mock_secret_client.return_value = mock_client_instance
    
    # Initialize provider
    provider = AzureKeyVaultProvider(
        vault_name="test-vault",
        tenant_id="test-tenant",
        client_id="test-client",
        client_secret="test-secret",
    )
    
    # Verify initialization
    assert provider.vault_name == "test-vault"
    assert provider.vault_url == "https://test-vault.vault.azure.net"
    
    # Verify Azure SDK was called
    mock_credential.assert_called_once_with(
        tenant_id="test-tenant",
        client_id="test-client",
        client_secret="test-secret",
    )


@patch("src.backend.core.secrets.ClientSecretCredential")
@patch("src.backend.core.secrets.SecretClient")
def test_azure_provider_get_secret(mock_secret_client, mock_credential):
    """Test getting secret from Azure Key Vault"""
    # Mock Azure SDK
    mock_secret = Mock()
    mock_secret.value = "secret_value_from_vault"
    
    mock_client_instance = Mock()
    mock_client_instance.get_secret.return_value = mock_secret
    mock_secret_client.return_value = mock_client_instance
    
    # Initialize provider
    provider = AzureKeyVaultProvider(
        vault_name="test-vault",
        tenant_id="test-tenant",
        client_id="test-client",
        client_secret="test-secret",
    )
    
    # Get secret
    value = provider.get_secret("JWT-SECRET-KEY")
    
    assert value == "secret_value_from_vault"
    mock_client_instance.get_secret.assert_called_once_with("JWT-SECRET-KEY")


@patch("src.backend.core.secrets.ClientSecretCredential")
@patch("src.backend.core.secrets.SecretClient")
def test_azure_provider_set_secret(mock_secret_client, mock_credential):
    """Test setting secret in Azure Key Vault"""
    mock_client_instance = Mock()
    mock_secret_client.return_value = mock_client_instance
    
    provider = AzureKeyVaultProvider(
        vault_name="test-vault",
        tenant_id="test-tenant",
        client_id="test-client",
        client_secret="test-secret",
    )
    
    # Set secret
    provider.set_secret("NEW-SECRET", "new_value")
    
    mock_client_instance.set_secret.assert_called_once_with("NEW-SECRET", "new_value")


@patch("src.backend.core.secrets.ClientSecretCredential")
@patch("src.backend.core.secrets.SecretClient")
def test_azure_provider_delete_secret(mock_secret_client, mock_credential):
    """Test deleting secret from Azure Key Vault"""
    mock_poller = Mock()
    mock_poller.wait.return_value = None
    
    mock_client_instance = Mock()
    mock_client_instance.begin_delete_secret.return_value = mock_poller
    mock_secret_client.return_value = mock_client_instance
    
    provider = AzureKeyVaultProvider(
        vault_name="test-vault",
        tenant_id="test-tenant",
        client_id="test-client",
        client_secret="test-secret",
    )
    
    # Delete secret
    provider.delete_secret("OLD-SECRET")
    
    mock_client_instance.begin_delete_secret.assert_called_once_with("OLD-SECRET")
    mock_poller.wait.assert_called_once()


@patch("src.backend.core.secrets.ClientSecretCredential")
@patch("src.backend.core.secrets.SecretClient")
def test_azure_provider_list_secrets(mock_secret_client, mock_credential):
    """Test listing secrets from Azure Key Vault"""
    # Mock secret properties
    mock_secret1 = Mock()
    mock_secret1.name = "SECRET-1"
    
    mock_secret2 = Mock()
    mock_secret2.name = "SECRET-2"
    
    mock_client_instance = Mock()
    mock_client_instance.list_properties_of_secrets.return_value = [
        mock_secret1,
        mock_secret2,
    ]
    mock_secret_client.return_value = mock_client_instance
    
    provider = AzureKeyVaultProvider(
        vault_name="test-vault",
        tenant_id="test-tenant",
        client_id="test-client",
        client_secret="test-secret",
    )
    
    # List secrets
    secrets = provider.list_secrets()
    
    assert secrets == ["SECRET-1", "SECRET-2"]


def test_azure_provider_missing_config():
    """Test error when Azure configuration is incomplete"""
    with pytest.raises(ValueError) as exc_info:
        AzureKeyVaultProvider(
            vault_name=None,  # Missing
            tenant_id="test-tenant",
            client_id="test-client",
            client_secret="test-secret",
        )
    
    assert "configuration incomplete" in str(exc_info.value).lower()


# ============================================================================
# Test Secrets Manager
# ============================================================================

def test_secrets_manager_with_environment_provider():
    """Test SecretsManager with environment provider"""
    provider = EnvironmentSecretsProvider()
    manager = SecretsManager(provider=provider)
    
    # Set test environment variable
    os.environ["TEST_SECRET"] = "test_value"
    
    # Get secret through manager
    value = manager.get_secret("TEST_SECRET")
    assert value == "test_value"
    
    # Cleanup
    del os.environ["TEST_SECRET"]


def test_secrets_manager_caching():
    """Test secrets caching in SecretsManager"""
    provider = EnvironmentSecretsProvider()
    manager = SecretsManager(provider=provider)
    
    # Set test environment variable
    os.environ["TEST_SECRET"] = "original_value"
    
    # Get secret (should cache)
    value1 = manager.get_secret("TEST_SECRET", use_cache=True)
    assert value1 == "original_value"
    
    # Change environment variable
    os.environ["TEST_SECRET"] = "new_value"
    
    # Get cached value (should return original)
    value2 = manager.get_secret("TEST_SECRET", use_cache=True)
    assert value2 == "original_value"
    
    # Get without cache (should return new value)
    value3 = manager.get_secret("TEST_SECRET", use_cache=False)
    assert value3 == "new_value"
    
    # Cleanup
    del os.environ["TEST_SECRET"]


def test_secrets_manager_cache_invalidation():
    """Test cache invalidation when setting secrets"""
    # Mock provider that supports set_secret
    mock_provider = Mock()
    mock_provider.get_secret.side_effect = ["value1", "value2"]
    mock_provider.set_secret.return_value = None
    
    manager = SecretsManager(provider=mock_provider)
    
    # Get secret (cache it)
    value1 = manager.get_secret("TEST_SECRET", use_cache=True)
    assert value1 == "value1"
    
    # Set secret (should invalidate cache)
    manager.set_secret("TEST_SECRET", "new_value")
    
    # Get secret again (should fetch fresh)
    value2 = manager.get_secret("TEST_SECRET", use_cache=True)
    assert value2 == "value2"


def test_secrets_manager_clear_cache():
    """Test clearing secrets cache"""
    provider = EnvironmentSecretsProvider()
    manager = SecretsManager(provider=provider)
    
    # Set test environment variable
    os.environ["TEST_SECRET"] = "original_value"
    
    # Cache secret
    manager.get_secret("TEST_SECRET", use_cache=True)
    
    # Change environment variable
    os.environ["TEST_SECRET"] = "new_value"
    
    # Clear cache
    manager.clear_cache()
    
    # Get secret (should return new value)
    value = manager.get_secret("TEST_SECRET", use_cache=True)
    assert value == "new_value"
    
    # Cleanup
    del os.environ["TEST_SECRET"]


# ============================================================================
# Test Auto-Detection
# ============================================================================

@patch.dict(os.environ, {}, clear=True)
def test_auto_detect_environment_provider():
    """Test auto-detection selects environment provider"""
    # Clear Azure Key Vault env vars
    manager = SecretsManager()
    
    assert isinstance(manager.provider, EnvironmentSecretsProvider)


@patch("src.backend.core.secrets.AzureKeyVaultProvider")
@patch.dict(os.environ, {
    "AZURE_KEY_VAULT_NAME": "test-vault",
    "AZURE_TENANT_ID": "test-tenant",
    "AZURE_CLIENT_ID": "test-client",
    "AZURE_CLIENT_SECRET": "test-secret",
}, clear=True)
def test_auto_detect_azure_provider(mock_azure_provider):
    """Test auto-detection selects Azure provider when configured"""
    mock_instance = Mock()
    mock_azure_provider.return_value = mock_instance
    
    manager = SecretsManager()
    
    # Should attempt to create Azure provider
    mock_azure_provider.assert_called_once()


# ============================================================================
# Test Convenience Functions
# ============================================================================

def test_get_secret_convenience_function():
    """Test get_secret convenience function"""
    # Set test environment variable
    os.environ["TEST_SECRET"] = "convenience_value"
    
    value = get_secret("TEST_SECRET")
    assert value == "convenience_value"
    
    # Cleanup
    del os.environ["TEST_SECRET"]


def test_get_secrets_manager_singleton():
    """Test get_secrets_manager returns singleton"""
    manager1 = get_secrets_manager()
    manager2 = get_secrets_manager()
    
    # Should be same instance
    assert manager1 is manager2


# ============================================================================
# Test Error Handling
# ============================================================================

@patch("src.backend.core.secrets.ClientSecretCredential")
@patch("src.backend.core.secrets.SecretClient")
def test_azure_provider_error_handling(mock_secret_client, mock_credential):
    """Test error handling in Azure provider"""
    mock_client_instance = Mock()
    mock_client_instance.get_secret.side_effect = Exception("Connection failed")
    mock_secret_client.return_value = mock_client_instance
    
    provider = AzureKeyVaultProvider(
        vault_name="test-vault",
        tenant_id="test-tenant",
        client_id="test-client",
        client_secret="test-secret",
    )
    
    with pytest.raises(ValueError) as exc_info:
        provider.get_secret("FAILING-SECRET")
    
    assert "failed to retrieve" in str(exc_info.value).lower()


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
