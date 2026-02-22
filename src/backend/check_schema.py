"""Check current schema"""
import sys
sys.path.insert(0, '.')
from controls.schemas import ControlResponse

print("ControlResponse model fields:")
for name, field_info in ControlResponse.model_fields.items():
    print(f"  {name}: {field_info.annotation} (required={field_info.is_required()})")
