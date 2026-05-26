import asyncpg
from src.config import settings

_pool: asyncpg.Pool | None = None


async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            dsn=settings.asyncpg_url,
            min_size=2,
            max_size=10,
        )
    return _pool


async def init_db():
    pool = await get_pool()
    async with pool.acquire() as conn:
        with open("src/db/schema.sql") as f:
            await conn.execute(f.read())


async def close_db():
    global _pool
    if _pool:
        await _pool.close()
        _pool = None
