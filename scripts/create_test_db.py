"""Create sico_grc_test database if it doesn't exist."""
import asyncio
import asyncpg

async def create_db():
    conn = await asyncpg.connect(
        host="localhost", user="postgres", password="root", database="postgres"
    )
    exists = await conn.fetchval(
        "SELECT 1 FROM pg_database WHERE datname=$1", "sico_grc_test"
    )
    print("DB exists:", exists)
    if not exists:
        await conn.execute("CREATE DATABASE sico_grc_test")
        print("Created sico_grc_test")
    else:
        print("sico_grc_test already exists")
    await conn.close()

asyncio.run(create_db())
