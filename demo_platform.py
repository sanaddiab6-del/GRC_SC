#!/usr/bin/env python3
"""
SICO GRC Platform - Professional Demo
Initializes database and demonstrates enterprise features

Usage: python demo_platform.py
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "src" / "backend"))

from sqlalchemy.ext.asyncio import AsyncSession
from core.database import AsyncSessionLocal, init_db, Base, engine


async def initialize_database():
    """Initialize database schema"""
    print("=" * 80)
    print("🏢 SICO Enterprise GRC Platform - Professional Demo")
    print("=" * 80)
    print("\n📊 Initializing database...")
    
    try:
        # Drop all tables first for clean slate
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            print("   ✓ Dropped existing tables")
        
        # Create all tables
        await init_db()
        print("   ✓ Created database schema")
        
        print("\n✅ Database initialized successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def load_demo_data():
    """Load comprehensive demo data"""
    print("\n📦 Loading demo data...")
    
    # Import after database is initialized
    from datetime import datetime, timedelta
    from auth.models import User, Role
    from auth.security import get_password_hash
    
    async with AsyncSessionLocal() as session:
        try:
            # Create Roles
            print("\n👤 Creating Roles...")
            roles_data = [
                ("admin", "System Administrator", "مدير النظام"),
                ("security_officer", "Chief Information Security Officer", "مسؤول  أمن المعلومات"),
                ("compliance_officer", "Compliance Officer", "مسؤول الامتثال"),
                ("auditor", "Internal Auditor", "مدقق داخلي"),
                ("risk_manager", "Risk Manager", "مدير المخاطر"),
                ("analyst", "Security Analyst", "محلل أمني"),
                ("viewer", "Read-Only Viewer", "مشاهد فقط"),
            ]
            
            for role_name, desc_en, desc_ar in roles_data:
                role = Role(
                    role_name=role_name,
                    description_en=desc_en,
                    description_ar=desc_ar
                )
                session.add(role)
                print(f"   ✓ Role: {role_name}")
            
            await session.flush()
            
            # Create Users
            print("\n👥 Creating Users...")
            users_data = [
                ("admin@snb.sa", "Admin User", "مدير النظام"),
                ("ciso@snb.sa", "Mohammed Al-Rashid", "محمد الراشد"),
                ("compliance@snb.sa", "Fatima Al-Qasim", "فاطمة القاسم"),
                ("auditor@snb.sa", "Ahmed Al-Mutairi", "أحمد المطيري"),
                ("risk@snb.sa", "Sara Al-Fahad", "سارة الفهد"),
                ("analyst@snb.sa", "Khalid Al-Shahrani", "خالد الشهراني"),
            ]
            
            for email, name_en, name_ar in users_data:
                user = User(
                    email=email,
                    password_hash=get_password_hash("Password123!"),
                    full_name_en=name_en,
                    full_name_ar=name_ar,
                    is_active=True,
                    is_verified=True
                )
                session.add(user)
                print(f"   ✓ User: {name_en} ({email})")
            
            await session.commit()
            print("\n✅ Demo data loaded successfully!")
            
        except Exception as e:
            await session.rollback()
            print(f"\n❌ Error loading demo data: {e}")
            import traceback
            traceback.print_exc()


async def verify_platform():
    """Verify platform is ready"""
    print("\n🔍 Verifying Platform...")
    
    from sqlalchemy import select, func
    from auth.models import User, Role
    
    async with AsyncSessionLocal() as session:
        # Count users
        result = await session.execute(select(func.count()).select_from(User))
        user_count = result.scalar()
        
        # Count roles
        result = await session.execute(select(func.count()).select_from(Role))
        role_count = result.scalar()
        
        print(f"   ✓ Users: {user_count}")
        print(f"   ✓ Roles: {role_count}")
    
    print("\n" + "=" * 80)
    print("✨ PLATFORM READY FOR DEMONSTRATION")
    print("=" * 80)
    print("\n🌐 Access Points:")
    print("   Frontend: http://localhost:3000")
    print("   Backend API: http://localhost:8000")
    print("   API Documentation: http://localhost:8000/docs")
    print("\n👥 Demo Credentials:")
    print("   Email: admin@snb.sa")
    print("   Password: Password123!")
    print("\n📚 Key Features to Demonstrate:")
    print("   ✓ Multi-framework compliance (NCA ECC/CCC, PDPL, ISO 27001)")  
    print("   ✓ Risk management with heat maps")
    print("   ✓ Asset inventory with criticality ratings")
    print("   ✓ Audit management and findings tracking")
    print("   ✓ PDPL compliance (RoPA, DSAR, Breach Management)")
    print("   ✓ Vendor risk assessments")
    print("   ✓ Policy management with versioning")
    print("   ✓ Security incident workflow")
    print("   ✓ Bil ingual support (English/Arabic)")
    print("   ✓ Role-based access control (RBAC)")
    print("   ✓ Comprehensive audit logging")
    print("=" * 80)


async def main():
    """Main demo setup"""
    # Step 1: Initialize database
    if not await initialize_database():
        sys.exit(1)
    
    # Step 2: Load demo data
    await load_demo_data()
    
    # Step 3: Verify platform
    await verify_platform()
    
    print("\n🚀 Demo platform is ready!")
    print("   Run the servers:")
    print("   Backend: cd src/backend && uvicorn main:app --reload")
    print("   Frontend: cd src/frontend && npm run dev")


if __name__ == "__main__":
    asyncio.run(main())
