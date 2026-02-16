"""
Test control serialization
"""
import asyncio
import sys
sys.path.insert(0, 'src/backend')

from sqlalchemy import select
from core.database import AsyncSessionLocal
from controls.models import Control
from controls.schemas import ControlResponse

async def test_serialization():
    async with AsyncSessionLocal() as db:
        try:
            query = select(Control).limit(1)
            result = await db.execute(query)
            control = result.scalar_one_or_none()
            
            if control:
                print(f"✓ Found control: {control.control_id}")
                print(f"  Framework type: {type(control.framework)}")
                print(f"  Framework value: {control.framework}")
                print(f"  Status type: {type(control.status)}")
                print(f"  Status value: {control.status}")
                
                # Try to serialize
                print("\nAttempting serialization...")
                response = ControlResponse.model_validate(control)
                print(f"✓ Successfully serialized!")
                print(f"  Response framework: {response.framework}")
                print(f"  Response status: {response.status}")
            else:
                print("✗ No controls found")
                
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_serialization())
