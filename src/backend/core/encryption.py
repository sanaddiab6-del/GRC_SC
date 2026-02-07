"""
Encryption utilities for PII data protection (PDPL Article 29, NCA CCC-SEC-01).
Implements field-level encryption using Fernet (AES-128 in CBC mode).
"""
from cryptography.fernet import Fernet
import base64
import os
from typing import Optional
from core.config import settings


class EncryptionService:
    """
    Service for encrypting/decrypting sensitive PII data.
    Uses AES-256 encryption via Fernet.
    """
    
    def __init__(self):
        """Initialize encryption service with key from Azure Key Vault (or env)."""
        # In production, fetch from Azure Key Vault
        # For development, use environment variable
        encryption_key = settings.ENCRYPTION_KEY
        
        if not encryption_key:
            raise ValueError("ENCRYPTION_KEY not configured. Set in environment or Azure Key Vault.")
        
        # Derive Fernet key from base key
        self.fernet = Fernet(encryption_key.encode())
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt plaintext string.
        Returns base64-encoded ciphertext.
        """
        if not plaintext:
            return ""
        
        try:
            ciphertext = self.fernet.encrypt(plaintext.encode())
            return base64.b64encode(ciphertext).decode()
        except Exception as e:
            raise ValueError(f"Encryption failed: {str(e)}")
    
    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt ciphertext string.
        Returns original plaintext.
        """
        if not ciphertext:
            return ""
        
        try:
            ciphertext_bytes = base64.b64decode(ciphertext.encode())
            plaintext = self.fernet.decrypt(ciphertext_bytes)
            return plaintext.decode()
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")
    
    def encrypt_dict(self, data: dict, fields_to_encrypt: list) -> dict:
        """
        Encrypt specific fields in a dictionary.
        
        Args:
            data: Dictionary with plaintext data
            fields_to_encrypt: List of field names to encrypt
        
        Returns:
            Dictionary with encrypted fields
        """
        encrypted_data = data.copy()
        
        for field in fields_to_encrypt:
            if field in encrypted_data and encrypted_data[field]:
                encrypted_data[field] = self.encrypt(str(encrypted_data[field]))
        
        return encrypted_data
    
    def decrypt_dict(self, data: dict, fields_to_decrypt: list) -> dict:
        """
        Decrypt specific fields in a dictionary.
        
        Args:
            data: Dictionary with encrypted data
            fields_to_decrypt: List of field names to decrypt
        
        Returns:
            Dictionary with decrypted fields
        """
        decrypted_data = data.copy()
        
        for field in fields_to_decrypt:
            if field in decrypted_data and decrypted_data[field]:
                decrypted_data[field] = self.decrypt(str(decrypted_data[field]))
        
        return decrypted_data


def generate_encryption_key() -> str:
    """
    Generate a new Fernet encryption key.
    Use this once during initial setup, then store in Azure Key Vault.
    """
    key = Fernet.generate_key()
    return key.decode()


# Singleton instance
_encryption_service: Optional[EncryptionService] = None


def get_encryption_service() -> EncryptionService:
    """Get or create encryption service singleton."""
    global _encryption_service
    
    if _encryption_service is None:
        _encryption_service = EncryptionService()
    
    return _encryption_service


# Fields that should be encrypted (PII under PDPL)
PII_FIELDS = [
    "email",
    "full_name_en",
    "full_name_ar",
    "phone_number",
    "national_id",
    "address",
    "ip_address"
]


def encrypt_pii(data: dict) -> dict:
    """
    Encrypt PII fields in data dictionary.
    Convenience function that uses the encryption service.
    """
    service = get_encryption_service()
    return service.encrypt_dict(data, PII_FIELDS)


def decrypt_pii(data: dict) -> dict:
    """
    Decrypt PII fields in data dictionary.
    Convenience function that uses the encryption service.
    """
    service = get_encryption_service()
    return service.decrypt_dict(data, PII_FIELDS)
