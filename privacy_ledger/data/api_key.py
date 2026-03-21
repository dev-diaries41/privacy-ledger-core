import asyncio
import asyncpg
import hashlib
from datetime import datetime, timezone
from typing import Optional, List

class APIKeyManager:
    """Async Postgres manager for API keys, using SHA-256 hash as ID."""

    def __init__(
        self,
        dsn: Optional[str] = None,
        host: Optional[str] = None,
        user: Optional[str] = None,
        port: int = 5432,
        password: Optional[str] = None,
        database: Optional[str] = None,
        min_pool_size: int = 1,
        max_pool_size: int = 10,
    ):
        if dsn is None:
            if not all([host, user, password, database]):
                raise ValueError("Either dsn or all of host, user, password, database must be provided")
            dsn = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        self.dsn = dsn
        self._pool: Optional[asyncpg.pool.Pool] = None
        self.min_pool_size = min_pool_size
        self.max_pool_size = max_pool_size
        self._lock = asyncio.Lock()
        self._init_done = False

    async def _init_db(self):
        if self._init_done:
            return
        if self._pool is None:
            self._pool = await asyncpg.create_pool(
                dsn=self.dsn, min_size=self.min_pool_size, max_size=self.max_pool_size
            )
        async with self._pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS api_keys (
                    key_hash TEXT PRIMARY KEY,
                    name TEXT,
                    scopes TEXT[],
                    created_at TIMESTAMP DEFAULT NOW(),
                    last_used_at TIMESTAMP
                )
            """)
        self._init_done = True

    @staticmethod
    def _hash_key(raw_key: str) -> str:
        return hashlib.sha256(raw_key.encode()).hexdigest()

    async def create(self, raw_key: str, name: Optional[str] = None, scopes: Optional[List[str]] = None):
        await self._init_db()
        key_hash = self._hash_key(raw_key)
        async with self._lock:
            async with self._pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO api_keys (key_hash, name, scopes)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (key_hash) DO NOTHING
                """, key_hash, name, scopes)

    async def validate(self, raw_key: str) -> Optional[dict]:
        """Return key metadata if valid, None if invalid."""
        await self._init_db()
        key_hash = self._hash_key(raw_key)
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM api_keys WHERE key_hash = $1", key_hash)
            if row:
                await conn.execute("UPDATE api_keys SET last_used_at = $1 WHERE key_hash = $2",
                                   datetime.now(timezone.utc) , key_hash)
                return dict(row)
            return None

    async def delete(self, raw_key: str):
        await self._init_db()
        key_hash = self._hash_key(raw_key)
        async with self._lock:
            async with self._pool.acquire() as conn:
                await conn.execute("DELETE FROM api_keys WHERE key_hash = $1", key_hash)