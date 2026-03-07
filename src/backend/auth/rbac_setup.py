"""
Initialize RBAC system with default roles and permissions.
Based on NCA ECC and PDPL requirements.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert
from auth.models import Role, Permission
from auth.models import role_permissions  # Import the junction table
import logging

logger = logging.getLogger(__name__)


# Default permissions matrix
DEFAULT_PERMISSIONS = [
    # Control permissions
    {"name": "controls:create", "resource": "controls", "action": "create",
     "desc_en": "Create new controls", "desc_ar": "إنشاء ضوابط جديدة"},
    {"name": "controls:read", "resource": "controls", "action": "read",
     "desc_en": "View controls", "desc_ar": "عرض الضوابط"},
    {"name": "controls:update", "resource": "controls", "action": "update",
     "desc_en": "Update controls", "desc_ar": "تحديث الضوابط"},
    {"name": "controls:delete", "resource": "controls", "action": "delete",
     "desc_en": "Delete controls", "desc_ar": "حذف الضوابط"},
    
    # Evidence permissions
    {"name": "evidence:create", "resource": "evidence", "action": "create",
     "desc_en": "Create evidence", "desc_ar": "إنشاء أدلة"},
    {"name": "evidence:read", "resource": "evidence", "action": "read",
     "desc_en": "View evidence", "desc_ar": "عرض الأدلة"},
    {"name": "evidence:update", "resource": "evidence", "action": "update",
     "desc_en": "Update evidence", "desc_ar": "تحديث الأدلة"},
    {"name": "evidence:delete", "resource": "evidence", "action": "delete",
     "desc_en": "Delete evidence", "desc_ar": "حذف الأدلة"},
    
    # Report permissions
    {"name": "reports:create", "resource": "reports", "action": "create",
     "desc_en": "Create reports", "desc_ar": "إنشاء تقارير"},
    {"name": "reports:read", "resource": "reports", "action": "read",
     "desc_en": "View reports", "desc_ar": "عرض التقارير"},
    {"name": "reports:update", "resource": "reports", "action": "update",
     "desc_en": "Update reports", "desc_ar": "تحديث التقارير"},
    {"name": "reports:delete", "resource": "reports", "action": "delete",
     "desc_en": "Delete reports", "desc_ar": "حذف التقارير"},
    
    # User management permissions
    {"name": "users:create", "resource": "users", "action": "create",
     "desc_en": "Create users", "desc_ar": "إنشاء مستخدمين"},
    {"name": "users:read", "resource": "users", "action": "read",
     "desc_en": "View users", "desc_ar": "عرض المستخدمين"},
    {"name": "users:update", "resource": "users", "action": "update",
     "desc_en": "Update users", "desc_ar": "تحديث المستخدمين"},
    {"name": "users:delete", "resource": "users", "action": "delete",
     "desc_en": "Delete users", "desc_ar": "حذف المستخدمين"},
    
    # Audit log permissions
    {"name": "audit:read", "resource": "audit", "action": "read",
     "desc_en": "View audit logs", "desc_ar": "عرض سجلات التدقيق"},
    
    # Backup and Disaster Recovery permissions (NCA ECC-BC-1, BC-2)
    {"name": "backup:create", "resource": "backup", "action": "create",
     "desc_en": "Create backups", "desc_ar": "إنشاء نسخ احتياطية"},
    {"name": "backup:read", "resource": "backup", "action": "read",
     "desc_en": "View backups", "desc_ar": "عرض النسخ الاحتياطية"},
    {"name": "backup:update", "resource": "backup", "action": "update",
     "desc_en": "Update backup status", "desc_ar": "تحديث حالة النسخ الاحتياطي"},
    {"name": "backup:delete", "resource": "backup", "action": "delete",
     "desc_en": "Delete expired backups", "desc_ar": "حذف النسخ الاحتياطية المنتهية"},
    {"name": "backup:test", "resource": "backup", "action": "test",
     "desc_en": "Conduct recovery tests", "desc_ar": "إجراء اختبارات الاسترداد"},
    
    # ISMS Policy permissions
    {"name": "isms:read", "resource": "isms", "action": "read",
     "desc_en": "View ISMS policies", "desc_ar": "عرض سياسات نظام إدارة أمن المعلومات"},
    {"name": "isms:write", "resource": "isms", "action": "write",
     "desc_en": "Create/update ISMS policies", "desc_ar": "إنشاء/تحديث سياسات ISMS"},
    {"name": "isms:approve", "resource": "isms", "action": "approve",
     "desc_en": "Approve ISMS policies", "desc_ar": "الموافقة على سياسات ISMS"},
    
    # Risk Management permissions (NCA ECC-RM)
    {"name": "risk:create", "resource": "risk", "action": "create",
     "desc_en": "Create new risks", "desc_ar": "إنشاء مخاطر جديدة"},
    {"name": "risk:read", "resource": "risk", "action": "read",
     "desc_en": "View risks", "desc_ar": "عرض المخاطر"},
    {"name": "risk:update", "resource": "risk", "action": "update",
     "desc_en": "Update risks", "desc_ar": "تحديث المخاطر"},
    {"name": "risk:delete", "resource": "risk", "action": "delete",
     "desc_en": "Delete risks", "desc_ar": "حذف المخاطر"},
    {"name": "risk:assess", "resource": "risk", "action": "assess",
     "desc_en": "Conduct risk assessments", "desc_ar": "إجراء تقييمات المخاطر"},
    {"name": "risk:manage", "resource": "risk", "action": "manage",
     "desc_en": "Manage third-party vendor risks", "desc_ar": "إدارة مخاطر الطرف الثالث"},
]


# Role definitions with permission mappings
DEFAULT_ROLES = {
    "Admin": {
        "desc_en": "System administrators with full access",
        "desc_ar": "مسؤولو النظام مع الوصول الكامل",
        "permissions": [
            "controls:create", "controls:read", "controls:update", "controls:delete",
            "evidence:create", "evidence:read", "evidence:update", "evidence:delete",
            "reports:create", "reports:read", "reports:update", "reports:delete",
            "users:create", "users:read", "users:update", "users:delete",
            "audit:read",
            "backup:create", "backup:read", "backup:update", "backup:delete", "backup:test",
            "isms:read", "isms:write", "isms:approve",
            "risk:create", "risk:read", "risk:update", "risk:delete", "risk:assess", "risk:manage"
        ]
    },
    "Compliance Officer": {
        "desc_en": "Manage compliance controls and evidence",
        "desc_ar": "إدارة ضوابط الامتثال والأدلة",
        "permissions": [
            "controls:create", "controls:read", "controls:update", "controls:delete",
            "evidence:create", "evidence:read", "evidence:update", "evidence:delete",
            "reports:read",
            "risk:create", "risk:read", "risk:update", "risk:assess"
        ]
    },
    "Auditor": {
        "desc_en": "Audit activities with read-only + evidence management",
        "desc_ar": "أنشطة التدقيق مع القراءة فقط + إدارة الأدلة",
        "permissions": [
            "controls:read",
            "evidence:create", "evidence:read", "evidence:update",
            "reports:read",
            "audit:read",
            "risk:read", "risk:assess"
        ]
    },
    "Analyst": {
        "desc_en": "Reporting and analysis with read-only access",
        "desc_ar": "التقارير والتحليل مع الوصول للقراءة فقط",
        "permissions": [
            "controls:read",
            "evidence:read",
            "reports:read",
            "risk:read"
        ]
    },
    "Viewer": {
        "desc_en": "Read-only access to public information",
        "desc_ar": "الوصول للقراءة فقط للمعلومات العامة",
        "permissions": [
            "controls:read",
            "reports:read",
            "risk:read"
        ]
    }
}


async def initialize_rbac(db: AsyncSession):
    """
    Initialize RBAC system with default roles and permissions.
    Safe to run multiple times (idempotent).
    """
    try:
        logger.info("Initializing RBAC system...")
        
        # Create permissions
        permission_map = {}
        for perm_data in DEFAULT_PERMISSIONS:
            result = await db.execute(
                select(Permission).where(Permission.permission_name == perm_data["name"])
            )
            existing_perm = result.scalar_one_or_none()
            
            if not existing_perm:
                new_perm = Permission(
                    permission_name=perm_data["name"],
                    resource=perm_data["resource"],
                    action=perm_data["action"],
                    description_en=perm_data["desc_en"],
                    description_ar=perm_data["desc_ar"]
                )
                db.add(new_perm)
                await db.flush()
                permission_map[perm_data["name"]] = new_perm
                logger.info(f"Created permission: {perm_data['name']}")
            else:
                permission_map[perm_data["name"]] = existing_perm
        
        await db.commit()
        
        # Create roles and assign permissions
        for role_name, role_data in DEFAULT_ROLES.items():
            result = await db.execute(
                select(Role).where(Role.role_name == role_name)
            )
            existing_role = result.scalar_one_or_none()
            
            if not existing_role:
                new_role = Role(
                    role_name=role_name,
                    description_en=role_data["desc_en"],
                    description_ar=role_data["desc_ar"]
                )
                db.add(new_role)
                await db.flush()
                
                # Assign permissions to role using direct insert
                for perm_name in role_data["permissions"]:
                    if perm_name in permission_map:
                        await db.execute(
                            insert(role_permissions).values(
                                role_id=new_role.role_id,
                                permission_id=permission_map[perm_name].permission_id
                            )
                        )
                
                logger.info(f"Created role: {role_name} with {len(role_data['permissions'])} permissions")
            else:
                # Update existing role permissions by deleting old and inserting new
                await db.execute(
                    role_permissions.delete().where(role_permissions.c.role_id == existing_role.role_id)
                )
                for perm_name in role_data["permissions"]:
                    if perm_name in permission_map:
                        await db.execute(
                            insert(role_permissions).values(
                                role_id=existing_role.role_id,
                                permission_id=permission_map[perm_name].permission_id
                            )
                        )
                logger.info(f"Updated role: {role_name}")
        
        await db.commit()
        logger.info("RBAC system initialized successfully")
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error initializing RBAC: {str(e)}")
        raise
