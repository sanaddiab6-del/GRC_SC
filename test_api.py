"""
Quick API test script
"""
import asyncio
import sys
sys.path.insert(0, 'src/backend')

from sqlalchemy import select
from core.database import AsyncSessionLocal
from controls.models import Control

async def test_controls():
    async with AsyncSessionLocal() as db:
        try:
            # Test query
            query = select(Control).limit(5)
            result = await db.execute(query)
            controls = result.scalars().all()
            
            print(f"✓ Successfully queried database")
            print(f"✓ Found {len(controls)} controls")
            
            if controls:
                for ctrl in controls:
                    print(f"  - {ctrl.control_id}: {ctrl.title_en}")
            else:
                print("⚠ No controls found in database")
                
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_controls())
