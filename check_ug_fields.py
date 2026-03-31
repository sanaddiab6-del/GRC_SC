import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ciso_assistant.settings')
django.setup()

from iam.models import UserGroup, User
ug = UserGroup.objects.first()

print("=== ALL FIELDS ===")
for f in ug._meta.get_fields():
    m2m = getattr(f, 'many_to_many', 'n/a')
    rel = getattr(f, 'related_model', None)
    fname = f.name
    ftype = type(f).__name__
    print(f"  {fname} | {ftype} | m2m={m2m} | related={rel}")

print("\n=== USER-RELATED ATTRS ===")
for attr in sorted(dir(ug)):
    if 'user' in attr.lower():
        print(f"  {attr}")

# Try the User model side
print("\n=== User model fields with 'group' ===")
u = User.objects.first()
if u:
    for f in u._meta.get_fields():
        if 'group' in f.name.lower():
            print(f"  {f.name} | {type(f).__name__}")
    for attr in sorted(dir(u)):
        if 'group' in attr.lower():
            print(f"  attr: {attr}")
