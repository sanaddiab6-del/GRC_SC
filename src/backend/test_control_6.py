"""Test serialization of control #6"""
import sys
sys.path.insert(0, '.')

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from controls.models import Control
from controls.schemas import ControlResponse

engine = create_engine('sqlite:///sico_grc.db')
session =Session(engine)

# Get control #6
control = session.execute(select(Control).where(Control.id == 6)).scalar_one()
print(f"Control ID: {control.control_id}")
print(f"Framework: {control.framework}")
print(f"Status: {control.status}")
print(f"Created: {control.created_at}")
print(f"Evidence types: {control.evidence_types}")
print(f"Related controls: {control.related_controls}")

# Try to serialize
try:
    response = ControlResponse.model_validate(control)
    print("✅ Serialization successful!")
    print(f"Response: {response.model_dump_json()[:200]}")
except Exception as e:
    print(f"❌ Serialization failed: {e}")
    import traceback
    traceback.print_exc()
