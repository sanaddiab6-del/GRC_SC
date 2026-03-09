"""
Tests for core/encryption.py — field-level encryption service.
"""
import pytest
from cryptography.fernet import Fernet


@pytest.fixture
def encryption_service():
    """Create an EncryptionService with a test key."""
    import os
    key = Fernet.generate_key().decode()
    os.environ["ENCRYPTION_KEY"] = key
    # Reset the singleton so it picks up the new key
    import core.encryption as enc_mod
    enc_mod._encryption_service = None
    from core.encryption import EncryptionService
    return EncryptionService()


def test_generate_encryption_key():
    from core.encryption import generate_encryption_key

    key = generate_encryption_key()
    assert isinstance(key, str)
    assert len(key) > 20
    # Valid Fernet key
    Fernet(key.encode())


def test_encrypt_decrypt_roundtrip(encryption_service):
    plaintext = "sensitive data"
    ciphertext = encryption_service.encrypt(plaintext)
    assert ciphertext != plaintext
    decrypted = encryption_service.decrypt(ciphertext)
    assert decrypted == plaintext


def test_encrypt_empty_string(encryption_service):
    assert encryption_service.encrypt("") == ""


def test_decrypt_empty_string(encryption_service):
    assert encryption_service.decrypt("") == ""


def test_encrypt_unicode(encryption_service):
    text = "بيانات حساسة"  # Arabic text
    ciphertext = encryption_service.encrypt(text)
    assert encryption_service.decrypt(ciphertext) == text


def test_encrypt_dict(encryption_service):
    data = {"email": "user@test.com", "name": "Test", "age": 30}
    encrypted = encryption_service.encrypt_dict(data, ["email"])
    assert encrypted["email"] != "user@test.com"
    assert encrypted["name"] == "Test"  # Unencrypted
    assert encrypted["age"] == 30


def test_decrypt_dict(encryption_service):
    data = {"email": "user@test.com", "name": "Test"}
    encrypted = encryption_service.encrypt_dict(data, ["email"])
    decrypted = encryption_service.decrypt_dict(encrypted, ["email"])
    assert decrypted["email"] == "user@test.com"
    assert decrypted["name"] == "Test"


def test_encrypt_dict_missing_field(encryption_service):
    data = {"name": "Test"}
    encrypted = encryption_service.encrypt_dict(data, ["email"])
    assert "email" not in encrypted
    assert encrypted["name"] == "Test"


def test_encrypt_dict_none_value(encryption_service):
    data = {"email": None, "name": "Test"}
    encrypted = encryption_service.encrypt_dict(data, ["email"])
    assert encrypted["email"] is None  # None stays None


def test_pii_fields_defined():
    from core.encryption import PII_FIELDS

    assert "email" in PII_FIELDS
    assert "full_name_en" in PII_FIELDS
    assert "national_id" in PII_FIELDS
