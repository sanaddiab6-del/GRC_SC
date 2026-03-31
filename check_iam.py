import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ciso_assistant.settings')
django.setup()

from iam.models import User, Folder, UserGroup, Role, RoleAssignment

print('=== SUPERUSERS ===')
for u in User.objects.filter(is_superuser=True):
    print(f'  {u.email} | active={u.is_active}')

print('\n=== ALL USERS ===')
for u in User.objects.all():
    print(f'  {u.email} | active={u.is_active} | super={u.is_superuser}')

print('\n=== FOLDERS ===')
for f in Folder.objects.all():
    parent = f.parent_folder.name if f.parent_folder else 'None'
    print(f'  {f.name} | type={f.content_type} | parent={parent}')

print('\n=== ROLES (builtin) ===')
for r in Role.objects.filter(builtin=True):
    tier = getattr(r, 'tier', 'n/a')
    print(f'  {r.name} | tier={tier} | perms={r.permissions.count()}')

print('\n=== USER GROUPS ===')
for ug in UserGroup.objects.all():
    folder_name = ug.folder.name if ug.folder else 'None'
    # Find the M2M field name
    m2m_fields = [f.name for f in ug._meta.get_fields() if f.many_to_many or (hasattr(f, 'related_model') and f.related_model == User)]
    print(f'  {ug.name} | builtin={ug.builtin} | folder={folder_name} | m2m_fields={m2m_fields}')

print('\n=== ROLE ASSIGNMENTS ===')
for ra in RoleAssignment.objects.all():
    user_email = ra.user.email if ra.user else 'None'
    ug_name = ra.user_group.name if ra.user_group else 'None'
    role_name = ra.role.name if ra.role else 'None'
    folders = [f.name for f in ra.perimeter_folders.all()]
    print(f'  role={role_name} | user={user_email} | group={ug_name} | folders={folders} | recursive={ra.is_recursive}')
