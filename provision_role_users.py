"""
Provision 7 demo users — one per built-in role tier — in the SICO GRC Platform.
Each user is assigned to a domain-level UserGroup with the corresponding role.
"""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ciso_assistant.settings')
django.setup()

from iam.models import User, Folder, UserGroup, Role, RoleAssignment

# ── Configuration ──────────────────────────────────────────────────
PASSWORD = 'Sico@2026!'  # Shared demo password so you can log in as each

# Map: role codename → (email, first_name, last_name, is_third_party)
ROLE_USERS = {
    'BI-RL-ADM': ('admin.role@sico.sa',       'Admin',    'User',      False),
    'BI-RL-DMA': ('domain.manager@sico.sa',   'Domain',   'Manager',   False),
    'BI-RL-ANA': ('analyst@sico.sa',          'Risk',     'Analyst',   False),
    'BI-RL-APP': ('approver@sico.sa',         'Compliance','Approver',  False),
    'BI-RL-AUD': ('auditor@sico.sa',          'Internal', 'Auditor',   False),
    'BI-RL-ADE': ('auditee@sico.sa',          'Business', 'Auditee',   False),
    'BI-RL-TPR': ('thirdparty@sico.sa',       'Vendor',   'Respondent',True),
}

# Role codename → UserGroup codename mapping
ROLE_TO_UG = {
    'BI-RL-ADM': 'BI-UG-ADM',
    'BI-RL-DMA': 'BI-UG-DMA',
    'BI-RL-ANA': 'BI-UG-ANA',
    'BI-RL-APP': 'BI-UG-APP',
    'BI-RL-AUD': 'BI-UG-AUD',
    'BI-RL-ADE': 'BI-UG-ADE',
    'BI-RL-TPR': 'BI-UG-ADM',  # Will handle separately
}

# ── Discover existing structure ────────────────────────────────────
root_folder = Folder.objects.get(content_type='GL')
domains = list(Folder.objects.filter(content_type='DO'))

print(f'Root folder: {root_folder.name}')
print(f'Domains: {[d.name for d in domains]}')
print()

roles = {r.name: r for r in Role.objects.filter(builtin=True)}
print('Built-in roles:')
for name, role in roles.items():
    perms = list(role.permissions.values_list('codename', flat=True))
    print(f'  {name}: {role.permissions.count()} permissions')

# The M2M is User.user_groups → UserGroup, so from User side: user.user_groups.add(ug)
print()

# ── Create users ───────────────────────────────────────────────────
print('\n=== CREATING USERS ===')

for role_code, (email, first_name, last_name, is_tp) in ROLE_USERS.items():
    # Create or get user
    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            'first_name': first_name,
            'last_name': last_name,
            'is_active': True,
            'is_superuser': (role_code == 'BI-RL-ADM'),
            'is_third_party': is_tp,
        }
    )
    if created:
        user.set_password(PASSWORD)
        user.first_login = False  # Skip first-login modal
        user.save()
        print(f'  CREATED: {email} ({first_name} {last_name}) [{"SUPERUSER" if user.is_superuser else role_code}]')
    else:
        print(f'  EXISTS:  {email}')

    # Assign to appropriate UserGroups
    role = roles.get(role_code)
    if not role:
        print(f'    WARNING: Role {role_code} not found!')
        continue

    ug_code = ROLE_TO_UG.get(role_code)

    if role_code == 'BI-RL-ADM':
        # Admin gets the Global-level admin group
        admin_groups = UserGroup.objects.filter(name='BI-UG-ADM', folder=root_folder)
        for ug in admin_groups:
            user.user_groups.add(ug)
            print(f'    Added to group: {ug.name} (folder: {ug.folder.name})')
    elif role_code == 'BI-RL-TPR':
        # Third-party: create a special assignment on the first domain
        if domains:
            domain = domains[0]
            # Direct user role assignment
            ra, ra_created = RoleAssignment.objects.get_or_create(
                user=user,
                role=role,
                folder=root_folder,
                defaults={
                    'name': f'TPR-{email}',
                    'builtin': False,
                    'is_recursive': True,
                }
            )
            if ra_created:
                ra.perimeter_folders.add(domain)
                print(f'    Direct RoleAssignment: {role.name} on {domain.name}')
            else:
                print(f'    RoleAssignment exists')
    else:
        # For other roles, add to domain-level groups for ALL domains
        target_groups = UserGroup.objects.filter(name=ug_code)
        for ug in target_groups:
            user.user_groups.add(ug)
            print(f'    Added to group: {ug.name} (folder: {ug.folder.name})')

# ── Print summary with permissions ─────────────────────────────────
print('\n' + '='*80)
print('ROLE HIERARCHY SUMMARY — PERMISSIONS PER ROLE')
print('='*80)

role_order = ['BI-RL-ADM', 'BI-RL-DMA', 'BI-RL-ANA', 'BI-RL-APP', 'BI-RL-AUD', 'BI-RL-ADE', 'BI-RL-TPR']
role_labels = {
    'BI-RL-ADM': 'Tier 1: Administrator',
    'BI-RL-DMA': 'Tier 2: Domain Manager',
    'BI-RL-ANA': 'Tier 3: Analyst',
    'BI-RL-APP': 'Tier 4: Approver',
    'BI-RL-AUD': 'Tier 5: Auditor (Reader)',
    'BI-RL-ADE': 'Tier 6: Auditee (Respondent)',
    'BI-RL-TPR': 'Tier 7: Third-Party Respondent',
}

for code in role_order:
    role = roles.get(code)
    if not role:
        continue
    perms = sorted(role.permissions.values_list('codename', flat=True))
    email = ROLE_USERS[code][0]
    print(f'\n{role_labels[code]}')
    print(f'  Email: {email}')
    print(f'  Password: {PASSWORD}')
    print(f'  Total Permissions: {len(perms)}')
    
    # Group by action type
    view_perms = [p for p in perms if p.startswith('view_')]
    add_perms = [p for p in perms if p.startswith('add_')]
    change_perms = [p for p in perms if p.startswith('change_')]
    delete_perms = [p for p in perms if p.startswith('delete_')]
    other_perms = [p for p in perms if not any(p.startswith(x) for x in ('view_', 'add_', 'change_', 'delete_'))]
    
    print(f'  Can VIEW ({len(view_perms)}):   {", ".join(p.replace("view_", "") for p in view_perms[:15])}{"..." if len(view_perms) > 15 else ""}')
    print(f'  Can CREATE ({len(add_perms)}):  {", ".join(p.replace("add_", "") for p in add_perms[:15])}{"..." if len(add_perms) > 15 else ""}')
    print(f'  Can EDIT ({len(change_perms)}):  {", ".join(p.replace("change_", "") for p in change_perms[:15])}{"..." if len(change_perms) > 15 else ""}')
    print(f'  Can DELETE ({len(delete_perms)}): {", ".join(p.replace("delete_", "") for p in delete_perms[:15])}{"..." if len(delete_perms) > 15 else ""}')
    if other_perms:
        print(f'  Special: {", ".join(other_perms)}')

# ── Verify assignments ─────────────────────────────────────────────
print('\n' + '='*80)
print('VERIFICATION — USER GROUP MEMBERSHIPS')
print('='*80)

for code in role_order:
    email = ROLE_USERS[code][0]
    user = User.objects.filter(email=email).first()
    if not user:
        print(f'\n  {email}: NOT FOUND')
        continue
    
    groups = []
    for ug in user.user_groups.all():
        groups.append(f'{ug.name}@{ug.folder.name}')
    
    direct_ras = RoleAssignment.objects.filter(user=user)
    ra_list = [f'{ra.role.name}→{[f.name for f in ra.perimeter_folders.all()]}' for ra in direct_ras]
    
    print(f'\n  {email}:')
    print(f'    Groups: {groups if groups else "None"}')
    print(f'    Direct RAs: {ra_list if ra_list else "None"}')
    print(f'    is_superuser: {user.is_superuser}')
    print(f'    is_third_party: {user.is_third_party}')

print('\n\nDone! You can now log in at https://localhost:8443 with any of these accounts.')
