from core.models import LoadedLibrary, Framework, RequirementNode, ReferenceControl
print("=== LOADED LIBRARIES ===")
libs = LoadedLibrary.objects.all()
for lib in libs:
    t = lib.translations or {}
    has_ar = 'ar' in t
    langs = list(t.keys())[:8]
    print(f"{lib.urn} | ar={has_ar} | langs={langs}")

print("\n=== FRAMEWORKS ===")
fws = Framework.objects.all()
for fw in fws:
    t = fw.translations or {}
    has_ar = 'ar' in t
    print(f"{fw.urn} | ar={has_ar} | langs={list(t.keys())[:8]}")

print("\n=== SAMPLE REQUIREMENT NODES (first 5) ===")
nodes = RequirementNode.objects.all()[:5]
for node in nodes:
    t = node.translations or {}
    has_ar = 'ar' in t
    print(f"{node.urn} | ar={has_ar} | name={node.name[:50] if node.name else 'N/A'}")

print("\n=== SAMPLE REFERENCE CONTROLS (first 5) ===")
ctrls = ReferenceControl.objects.all()[:5]
for ctrl in ctrls:
    t = ctrl.translations or {}
    has_ar = 'ar' in t
    print(f"{ctrl.urn} | ar={has_ar} | name={ctrl.name[:50] if ctrl.name else 'N/A'}")
