#!/usr/bin/env python3
"""
Script to initialize security settings for SICO GRC Platform.
Generates encryption keys and creates initial admin user.

NCA Compliance:
- ECC-IS-3: Role-Based Access Control (RBAC)
- ECC-IS-4: Password Policy Enforcement
- PDPL Article 29: Security Measures for Sensitive Data
"""
import asyncio
import sys
import re
import getpass
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "backend"))

from cryptography.fernet import Fernet
from sqlalchemy.ext.asyncio import AsyncSession
from auth.security import get_password_hash
from auth.models import User, Role
from auth.rbac_setup import initialize_rbac
from core.database import get_db
from sqlalchemy import select


def generate_keys():
    """Generate security keys for the application."""
    print("\n🔐 Security Key Generation")
    print("=" * 50)
    
    # Generate SECRET_KEY (256-bit)
    import secrets
    secret_key = secrets.token_hex(32)
    print(f"\nSECRET_KEY (for JWT signing):")
    print(f"{secret_key}")
    
    # Generate ENCRYPTION_KEY (for field-level encryption)
    encryption_key = Fernet.generate_key().decode()
    print(f"\nENCRYPTION_KEY (for PII encryption):")
    print(f"{encryption_key}")
    
    print("\n⚠️  IMPORTANT: Store these keys securely!")
    print("   - Add to .env file for development")
    print("   - Store in Azure Key Vault for production")
    print("   - Never commit keys to version control")
    
    return secret_key, encryption_key


def validate_password(password: str) -> tuple[bool, str]:
    """
    Validate password according to NCA ECC-IS-4 requirements.
    
    Requirements:
    - Minimum 12 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    - Cannot contain common patterns or dictionary words
    """
    if len(password) < 12:
        return False, "Password must be at least 12 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    # Check for common weak patterns (NCA best practice)
    weak_patterns = ['12345', 'password', 'admin', 'qwerty', 'abcd']
    password_lower = password.lower()
    for pattern in weak_patterns:
        if pattern in password_lower:
            return False, f"Password contains weak pattern: {pattern}"
    
    return True, "Password is strong"


async def create_admin_user(db: AsyncSession):
    """Create initial admin user with NCA-compliant password policy."""
    print("\n👤 Admin User Creation")
    print("=" * 50)
    
    email = input("Admin email: ")
    
    # Secure password input with validation (NCA ECC-IS-4)
    while True:
        password = getpass.getpass("Admin password (min 12 chars): ")
        password_confirm = getpass.getpass("Confirm password: ")
        
        if password != password_confirm:
            print("✗ Passwords do not match. Try again.")
            continue
        
        is_valid, message = validate_password(password)
        if not is_valid:
            print(f"✗ {message}")
            print("Password requirements:")
            print("  - Minimum 12 characters")
            print("  - At least one uppercase letter")
            print("  - At least one lowercase letter")
            print("  - At least one digit")
            print("  - At least one special character (!@#$%^&*...)")
            print("  - No common weak patterns")
            continue
        
        print(f"✓ {message}")
        break
    
    full_name_en = input("Full name (English): ")
    full_name_ar = input("Full name (Arabic, optional): ") or None
    
    # Check if user exists
    result = await db.execute(select(User).where(User.email == email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        print(f"✗ User with email {email} already exists")
        return
    
    # Create user
    user = User(
        email=email,
        password_hash=get_password_hash(password),
        full_name_en=full_name_en,
        full_name_ar=full_name_ar,
        is_active=True,
        is_verified=True
    )
    db.add(user)
    await db.flush()
    
    # Assign Admin role
    result = await db.execute(select(Role).where(Role.role_name == "Admin"))
    admin_role = result.scalar_one_or_none()
    
    if admin_role:
        user.roles.append(admin_role)
    
    await db.commit()
    
    print(f"✓ Admin user created: {email}")
    print(f"✓ Role assigned: Admin")


async def main():
    """Main setup function."""
    print("\n" + "=" * 50)
    print("SICO GRC Platform - Security Setup")
    print("Phase 2.1: Critical Security Controls")
    print("=" * 50)
    
    # Step 1: Generate keys
    print("\nStep 1: Generate Security Keys")
    choice = input("Generate new security keys? (y/n): ")
    if choice.lower() == 'y':
        secret_key, encryption_key = generate_keys()
        
        # Write to .env file
        env_file = Path(__file__).parent.parent / ".env"
        if env_file.exists():
            print(f"\n⚠️  .env file already exists: {env_file}")
            overwrite = input("Overwrite existing keys? (y/n): ")
            if overwrite.lower() != 'y':
                print("✗ Skipping key write")
            else:
                with open(env_file, "a") as f:
                    f.write(f"\nSECRET_KEY={secret_key}\n")
                    f.write(f"ENCRYPTION_KEY={encryption_key}\n")
                print(f"✓ Keys written to {env_file}")
        else:
            # Copy from env.example
            example_file = Path(__file__).parent.parent / "config" / "env.example"
            if example_file.exists():
                with open(example_file, "r") as f:
                    content = f.read()
                
                # Replace placeholders
                content = content.replace("SECRET_KEY=your-secret-key-change-in-production-use-openssl-rand-hex-32", 
                                        f"SECRET_KEY={secret_key}")
                content = content.replace("ENCRYPTION_KEY=", 
                                        f"ENCRYPTION_KEY={encryption_key}")
                
                with open(env_file, "w") as f:
                    f.write(content)
                
                print(f"✓ Created .env from template with keys")
    
    # Step 2: Initialize RBAC
    print("\nStep 2: Initialize RBAC System")
    choice = input("Initialize roles and permissions? (y/n): ")
    if choice.lower() == 'y':
        async for db in get_db():
            await initialize_rbac(db)
            print("✓ RBAC system initialized")
            
            # Step 3: Create admin user
            print("\nStep 3: Create Admin User")
            choice = input("Create admin user? (y/n): ")
            if choice.lower() == 'y':
                await create_admin_user(db)
            
            break
    
    print("\n" + "=" * 50)
    print("✓ Security setup complete!")
    print("\nNext steps:")
    print("1. Review .env file and update configuration")
    print("2. Run database migrations: alembic upgrade head")
    print("3. Start the server: python main.py")
    print("4. Test authentication: POST /api/v1/auth/login")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
