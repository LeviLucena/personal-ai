import asyncio
import os

import asyncpg


async def apply_schema(schema_path: str, dsn: str):
    with open(schema_path) as f:
        sql = f.read()
    conn = await asyncpg.connect(dsn)
    try:
        await conn.execute(sql)
    finally:
        await conn.close()


async def main():
    dsn = os.environ.get(
        "DATABASE_URL",
        "postgresql://personalai:personalai_secret@localhost:5432/personalai",
    )
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    print(f"Applying schema from {schema_path}...")
    await apply_schema(schema_path, dsn)
    print("Schema applied successfully.")


if __name__ == "__main__":
    asyncio.run(main())
