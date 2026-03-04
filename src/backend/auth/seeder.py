"""
Startup seeder – creates the default super_admin user and role if they
do not yet exist.

Idempotent: safe to run on every application startup.
"""
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from auth.models import User, Role, user_roles
from auth.security import get_password_hash

logger = logging.getLogger(__name__)

# ── Seeded credentials (override via environment in production) ──────────────
_ADMIN_EMAIL: str = "admin@grc.com"
_ADMIN_PASSWORD: str = "Admin@123"
_ADMIN_FULL_NAME_EN: str = "System Administrator"
_ADMIN_FULL_NAME_AR: str = "مدير النظام"
_ADMIN_ROLE: str = "super_admin"


async def seed_admin_user(db: AsyncSession) -> None:
    """
    Ensure a super_admin user and its role exist in the database.

    Steps
    -----
    1. Create the ``super_admin`` role if missing.
    2. Create the admin user if no users exist yet (email unique-check).
    3. Assign the role to the admin user if not already assigned.
    """
    try:
        # ── 1. Ensure super_admin role exists ────────────────────────────────
        result = await db.execute(
            select(Role).where(Role.role_name == _ADMIN_ROLE)
        )
        role = result.scalar_one_or_none()

        if role is None:
            role = Role(
                role_name=_ADMIN_ROLE,
                description_en="Super Administrator – full system access",
                description_ar="مدير النظام – وصول كامل",
            )
            db.add(role)
            await db.flush()  # get role_id without committing
            logger.info("✓ Created role: %s", _ADMIN_ROLE)

        # ── 2. Ensure admin user exists ──────────────────────────────────────
        result = await db.execute(
            select(User).where(User.email == _ADMIN_EMAIL)
        )
        user = result.scalar_one_or_none()

        if user is None:
            user = User(
                email=_ADMIN_EMAIL,
                password_hash=get_password_hash(_ADMIN_PASSWORD),
                full_name_en=_ADMIN_FULL_NAME_EN,
                full_name_ar=_ADMIN_FULL_NAME_AR,
                is_active=True,
                is_verified=True,
            )
            db.add(user)
            await db.flush()  # get user_id without committing
            logger.info("✓ Created admin user: %s", _ADMIN_EMAIL)

        # ── 3. Assign role if not already present ────────────────────────────
        # Reload user with roles eagerly to avoid async lazy-load issue
        result = await db.execute(
            select(User)
            .where(User.email == _ADMIN_EMAIL)
            .options(selectinload(User.roles))
        )
        user = result.scalar_one_or_none()

        role_names = [r.role_name for r in (user.roles if user else [])]
        if _ADMIN_ROLE not in role_names and user is not None:
            result = await db.execute(
                select(Role).where(Role.role_name == _ADMIN_ROLE)
            )
            role_obj = result.scalar_one_or_none()
            if role_obj is not None:
                user.roles.append(role_obj)
                logger.info(
                    "✓ Assigned role '%s' to %s", _ADMIN_ROLE, _ADMIN_EMAIL
                )

        await db.commit()
        logger.info("✓ Admin seeder complete – %s is ready", _ADMIN_EMAIL)

    except Exception as exc:  # noqa: BLE001
        await db.rollback()
        logger.warning("⚠️ Admin seeder encountered an issue: %s", exc)
        raise
