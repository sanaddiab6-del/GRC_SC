"""Test async database connectivity"""
import asyncio
from sqlalchemy import text
from core.database import AsyncSessionLocal

async def test_query():
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT COUNT(*) FROM organizations"))
        count = (result.fetchone() or (0,))[0]
        print(f"✓ Database query successful! Found {count} organizations")
        return count

if __name__ == "__main__":
    count = asyncio.run(test_query())
    print(f"Total organizations: {count}")
