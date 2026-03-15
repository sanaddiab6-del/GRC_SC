from core.models import RequirementNode
# Check is untranslated nodes have empty name/description
untranslated = RequirementNode.objects.exclude(translations__has_key='ar')
empty = untranslated.filter(name='', description='').count()
null_name = untranslated.filter(name__isnull=True).count()
print(f'Untranslated: {untranslated.count()}')
print(f'  Empty name+desc: {empty}')
print(f'  Null name: {null_name}')
# Show a few samples
for n in untranslated[:5]:
    print(f'  Sample: name="{n.name}" desc="{n.description[:50] if n.description else None}"')
