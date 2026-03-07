"""Check if risk permissions exist in database."""
import asyncio
import sys
sys.path.insert(0, r"C:\Projects\sico_grc\sanadcom\src\backend")

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import AsyncSessionLocal
from auth.models import Permission, Role, role_permissions


async def check_permissions():
    """Check if risk permissions exist and are assigned to roles."""
    async with AsyncSessionLocal() as db:
        # Check risk permissions
        result = await db.execute(
            select(Permission).where(Permission.resource == "risk")
        )
        risk_perms = result.scalars().all()
        
        print("=" * 60)
        print("RISK PERMISSIONS IN DATABASE")
        print("=" * 60)
        print(f"Total risk permissions: {len(risk_perms)}\n")
        
        if not risk_perms:
            print("❌ NO RISK PERMISSIONS FOUND!")
            print("The initialize_rbac function may not have run successfully.")
            return
        
        for perm in risk_perms:
            print(f"✓ {perm.permission_name}")
            print(f"  Resource: {perm.resource}, Action: {perm.action}")
            print(f"  Description: {perm.description_en}")
        
        # Check which roles have risk permissions
        print("\n" + "=" * 60)
        print("ROLES WITH RISK PERMISSIONS")
        print("=" * 60)
        
        result = await db.execute(select(Role))
        roles = result.scalars().all()
        
        for role in roles:
            # Get role's permissions
            result = await db.execute(
                select(Permission)
                .join(role_permissions, Permission.permission_id == role_permissions.c.permission_id)
                .where(role_permissions.c.role_id == role.role_id)
                .where(Permission.resource == "risk")
            )
            role_risk_perms = result.scalars().all()
            
            if role_risk_perms:
                print(f"\n{role.role_name}:")
                for perm in role_risk_perms:
                    print(f"  ✓ {perm.permission_name}")
            else:
                print(f"\n{role.role_name}: ❌ No risk permissions")


if __name__ == "__main__":
    asyncio.run(check_permissions())
