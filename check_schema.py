from sqlalchemy import create_engine, inspect
import sys

try:
    engine = create_engine('postgresql://postgres:postgres@localhost/sico_grc')
    inspector = inspect(engine)

    print("workflow_states columns:")
    cols = inspector.get_columns('workflow_states')
    for c in cols:
        print(f"  {c['name']}: {c['type']}")
        
    print("\nworkflow_transitions columns:")
    cols2 = inspector.get_columns('workflow_transitions')
    for c in cols2:
        print(f"  {c['name']}: {c['type']}")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
