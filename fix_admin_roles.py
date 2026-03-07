"""Assign Admin role to admin users who don't have roles."""
import asyncio
import sys
sys.path.insert(0, r"C:\Projects\sico_grc\sanadcom\src\backend")

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import AsyncSessionLocal
from auth.models import User, Role, user_roles


async def assign_admin_roles():
    """Assign Admin role to admin users."""
    async with AsyncSessionLocal() as db:
        print("=" * 60)
        print("ASSIGNING ADMIN ROLES")
        print("=" * 60)
        
        # Get Admin role
        result = await db.execute(
            select(Role).where(Role.role_name == "Admin")
        )
        admin_role = result.scalar_one_or_none()
        
        if not admin_role:
            print("❌ Admin role not found! Run RBAC initialization first.")
            return
        
        print(f"✓ Found Admin role: {admin_role.role_id}")
        
        # Get admin users (by email pattern)
        admin_emails = ["admin@grc.com", "admin@sanadcom.sa"]
        
        for email in admin_emails:
            result = await db.execute(
                select(User).where(User.email == email)
            )
            user =result.scalar_one_or_none()
            
            if not user:
                print(f"⚠️  User {email} not found, skipping")
                continue
            
            # Check if user already has Admin role
            result = await db.execute(
                select(user_roles)
                .where(user_roles.c.user_id == user.user_id)
                .where(user_roles.c.role_id == admin_role.role_id)
            )
            existing = result.first()
            
            if existing:
                print(f"✓ {email} already has Admin role")
                continue
            
            # Assign Admin role
            await db.execute(
                user_roles.insert().values(
                    user_id=user.user_id,
                    role_id=admin_role.role_id
                )
            )
            await db.commit()
            print(f"✅ Assigned Admin role to {email}")
        
        # Also check all users and assign roles to those without any
        result = await db.execute(select(User).where(User.is_active == True))
        all_users = result.scalars().all()
        
        # Get Viewer role for default assignment
        result = await db.execute(
            select(Role).where(Role.role_name == "Viewer")
        )
        viewer_role = result.scalar_one_or_none()
        
        print("\n" + "=" * 60)
        print("CHECKING ALL USERS")
        print("=" * 60)
        
        for user in all_users:
            result = await db.execute(
                select(user_roles).where(user_roles.c.user_id == user.user_id)
            )
            has_roles = result.first()
            
            if not has_roles and viewer_role:
                # Assign Viewer role to users without any role
                await db.execute(
                    user_roles.insert().values(
                        user_id=user.user_id,
                        role_id=viewer_role.role_id
                    )
                )
                await db.commit()
                print(f"✅ Assigned Viewer role to {user.email}")
            elif has_roles:
                print(f"✓ {user.email} has role assigned")
            else:
                print(f"⚠️  {user.email} - no role (Viewer role not found)")


if __name__ == "__main__":
    try:
        asyncio.run(assign_admin_roles())
        print("\n" + "=" * 60)
        print("✅ ROLE ASSIGNMENT COMPLETE!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Restart the backend")
        print("2. Clear browser sessionStorage")
        print("3. Login again to get fresh token with permissions")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
