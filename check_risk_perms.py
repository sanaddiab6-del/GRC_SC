import asyncio
from sqlalchemy import create_engine, text

# Simple sync check for risk permissions
engine = create_engine('postgresql://postgres:postgres@localhost:5432/sico_grc')

with engine.connect() as conn:
    result = conn.execute(text("SELECT permission_name FROM permissions WHERE resource = 'risk' ORDER BY action"))
    risk_perms = [row[0] for row in result]
    print(f"Risk permissions in database: {risk_perms}")
    
    if risk_perms:
        print("\n✓ Risk permissions found!")
    else:
        print("\n✗ No risk permissions found - RBAC needs to be reinitialized")
    
    # Check which roles have risk:read permission
    result2 = conn.execute(text("""
        SELECT r.role_name, p.permission_name
        FROM roles r
        JOIN role_permissions rp ON r.id = rp.role_id
        JOIN permissions p ON rp.permission_id = p.id
        WHERE p.resource = 'risk'
        ORDER BY r.role_name, p.action
    """))
    
    print("\nRoles with risk permissions:")
    for row in result2:
        print(f"  {row[0]}: {row[1]}")
