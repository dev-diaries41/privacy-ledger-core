import asyncio
import asyncpg

from typing import List, Optional, Literal
from datetime import date

from privacy_ledger.schema.events import PrivacyEvent, Topic, Severity, Scope, ImpactType, Filter, Platform


class EventStore:
    """Async Postgres store for PrivacyEvent with pgvector support, using a connection pool."""

    def __init__(
        self,
        embed_dim: int,
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
        self.embed_dim = embed_dim
        self._lock = asyncio.Lock()
        self._init_done = False
        self._pool: Optional[asyncpg.pool.Pool] = None
        self.min_pool_size = min_pool_size
        self.max_pool_size = max_pool_size

    async def _init_db(self):
        if self._init_done:
            return
        if self._pool is None:
            self._pool = await asyncpg.create_pool(
                dsn=self.dsn, min_size=self.min_pool_size, max_size=self.max_pool_size
            )
        async with self._pool.acquire() as conn:
            await conn.execute(f"""
                CREATE TABLE IF NOT EXISTS privacy_events (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    date DATE NOT NULL,
                    topic TEXT NOT NULL,
                    actors TEXT[] NOT NULL,
                    impact_types TEXT[] NOT NULL,
                    severity INT NOT NULL,
                    scope TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    impact_description TEXT NOT NULL,
                    source TEXT NOT NULL,
                    tags TEXT[],
                    platforms TEXT[],
                    embedding VECTOR({self.embed_dim}),
                    created_at DATE,
                    updated_at DATE
                )
            """)
        self._init_done = True
        await self._create_indexes()

    async def _create_indexes(self) -> None:
        """Create indexes to optimize queries on privacy_events table, including HNSW for embeddings."""
        await self._init_db()
        async with self._lock:
            async with self._pool.acquire() as conn:
                # B-tree indexes
                await conn.execute("CREATE INDEX IF NOT EXISTS idx_privacy_events_category ON privacy_events(topic)")
                await conn.execute("CREATE INDEX IF NOT EXISTS idx_privacy_events_severity ON privacy_events(severity)")
                await conn.execute("CREATE INDEX IF NOT EXISTS idx_privacy_events_scope ON privacy_events(scope)")
                await conn.execute("CREATE INDEX IF NOT EXISTS idx_privacy_events_created_at ON privacy_events(created_at)")
                await conn.execute("CREATE INDEX IF NOT EXISTS idx_privacy_events_updated_at ON privacy_events(updated_at)")

                # GIN indexes for array fields
                await conn.execute("CREATE INDEX IF NOT EXISTS idx_privacy_events_impact_types ON privacy_events USING GIN(impact_types)")
                await conn.execute("CREATE INDEX IF NOT EXISTS idx_privacy_events_tags ON privacy_events USING GIN(tags)")
                await conn.execute("CREATE INDEX IF NOT EXISTS idx_privacy_events_actors ON privacy_events USING GIN(actors)")
                await conn.execute("CREATE INDEX IF NOT EXISTS idx_privacy_events_platforms ON privacy_events USING GIN(platforms)")

                # pgvector HNSW index for embedding
                await conn.execute(f"""
                    CREATE INDEX IF NOT EXISTS idx_privacy_events_embedding
                    ON privacy_events USING hnsw (embedding vector_l2_ops)
                """)

    async def add(self, items: List[PrivacyEvent],embeddings: Optional[List[List[float]]] = None) -> None:
        if not items:
            return

        await self._init_db()

        async with self._lock:
            async with self._pool.acquire() as conn:
                data = []
                keys = list(items[0].model_dump(mode="json").keys())

                for i, event in enumerate(items):
                    embedding = embeddings[i] if embeddings else None
                    event_dict = event.model_dump()
                    event_dict.update({
                        "embedding": embedding,
                        "source": str(event_dict.get("source")),
                        "topic": event.topic.value,
                        "severity": event.severity.value,
                        "scope": event.scope.value,
                        "impact_types": [it.value for it in event.impact_types],
                        "platforms": [p.value for p in event.platforms],
                    })

                    data.append(tuple(event_dict[k] for k in keys))

                await conn.executemany(
                    f"""
                    INSERT INTO privacy_events ({', '.join(keys)})
                    VALUES ({','.join(f"${i+1}" for i in range(len(keys)))})
                    ON CONFLICT (id) DO NOTHING
                    """,
                    data
                )

    async def get(
        self,
        filter: Optional[Filter] = None ,
        limit: Optional[int] = 100,
        offset: int = 0,
        order_by: Literal["created_at", "updated_at", "date", "id"] = "created_at",
        ascending: bool = True,
    ) -> List[PrivacyEvent]:
        await self._init_db()
        async with self._pool.acquire() as conn:
            query = "SELECT * FROM privacy_events WHERE TRUE"
            filter = filter or Filter()
            query, params = self._add_filters(query, filter)
            order_clause = f" ORDER BY {order_by} {'ASC' if ascending else 'DESC'}"
            query += order_clause
            if limit is not None:
                query += f" LIMIT {limit} OFFSET {offset}"

            rows = await conn.fetch(query, *params)
            return [
                PrivacyEvent(
                    id=r["id"],
                    title=r["title"],
                    date=r["date"],
                    topic=Topic(r["topic"]),
                    actors=r["actors"],
                    impact_types=[ImpactType(it) for it in r["impact_types"]],
                    platforms=[Platform(p) for p in r["platforms"]],
                    severity=Severity(r["severity"]),
                    scope=Scope(r["scope"]),
                    summary=r["summary"],
                    impact_description=r["impact_description"],
                    source=r["source"],
                    tags=r["tags"],
                    created_at=r["created_at"],
                    updated_at=r["updated_at"]
                )
                for r in rows
            ]

    async def get_by_ids(self, ids: List[str]) -> List[PrivacyEvent]:
        if not ids:
            return []
        await self._init_db()
        async with self._pool.acquire() as conn:
            placeholders = ",".join(f"${i+1}" for i in range(len(ids)))
            query = f"SELECT * FROM privacy_events WHERE id IN ({placeholders})"
            rows = await conn.fetch(query, *ids)
            return [
                PrivacyEvent(
                    id=r["id"],
                    title=r["title"],
                    date=r["date"],
                    topic=Topic(r["topic"]),
                    actors=r["actors"],
                    impact_types=[ImpactType(it) for it in r["impact_types"]],
                    platforms=[Platform(p) for p in r["platforms"]],
                    severity=Severity(r["severity"]),
                    scope=Scope(r["scope"]),
                    summary=r["summary"],
                    impact_description=r["impact_description"],
                    source=r["source"],
                    tags=r["tags"],
                    created_at=r["created_at"],
                    updated_at=r["updated_at"]
                )
                for r in rows
            ]

    
    async def update(self,items: List[PrivacyEvent],embeddings: Optional[List[List[float]]] = None) -> None:
        if not items:
            return

        await self._init_db()

        async with self._lock:
            async with self._pool.acquire() as conn:
                for i, event in enumerate(items):
                    embedding = embeddings[i] if embeddings else None

                    await conn.execute("""
                        UPDATE privacy_events
                        SET title = $title,
                            date = $date,
                            topic = $topic,
                            actors = $actors,
                            impact_types = $impact_types,
                            platforms = $platforms,
                            severity = $severity,
                            scope = $scope,
                            summary = $summary,
                            impact_description = $impact_description,
                            source = $source,
                            tags = $tags,
                            embedding = $embedding,
                            updated_at = $updated_at
                        WHERE id = $id
                    """,
                        title=event.title,
                        date=event.date,
                        topic=event.topic.value,
                        actors=event.actors,
                        impact_types=[it.value for it in event.impact_types],
                        platforms=event.platforms,
                        severity=event.severity.value,
                        scope=event.scope.value,
                        summary=event.summary,
                        impact_description=event.impact_description,
                        source=event.source,
                        tags=event.tags,
                        embedding=embedding,
                        updated_at=event.updated_at or date.today(),
                        id=event.id
                    )

    async def delete(self, ids: List[str]) -> None:
        if not ids:
            return
        await self._init_db()
        async with self._lock:
            async with self._pool.acquire() as conn:
                placeholders = ",".join(f"${i+1}" for i in range(len(ids)))
                query = f"DELETE FROM privacy_events WHERE id IN ({placeholders})"
                await conn.execute(query, *ids)

    async def count(self, filter: Optional[Filter] = None) -> int:
        await self._init_db()
        async with self._pool.acquire() as conn:
            query = "SELECT COUNT(*) AS count FROM privacy_events WHERE TRUE"
            filter = filter or Filter()
            query, params = self._add_filters(query, filter)
            row = await conn.fetchrow(query, *params)
            return row["count"]
    
    @staticmethod
    def _add_filters(query: str, filter: Filter):
        params = []

        if filter.topic:
            query += f" AND topic = ${len(params)+1}"
            params.append(filter.topic)
        if filter.tags:
            query += f" AND tags @> ${len(params)+1}"
            params.append(filter.tags)
        if filter.actors:
            query += f" AND actors @> ${len(params)+1}"
            params.append(filter.actors)
        if filter.impact_types:
            query += f" AND impact_types @> ${len(params)+1}"
            params.append(filter.impact_types)
        if filter.platforms:
            query += f" AND platforms @> ${len(params)+1}"
            params.append(filter.platforms)
        if filter.severity is not None:
            query += f" AND severity = ${len(params)+1}"
            params.append(filter.severity)
        if filter.scope:
            query += f" AND scope = ${len(params)+1}"
            params.append(filter.scope)
        if filter.created_after:
            query += f" AND created_at >= ${len(params)+1}"
            params.append(filter.created_after)
        if filter.created_before:
            query += f" AND created_at <= ${len(params)+1}"
            params.append(filter.created_before)
        if filter.updated_after:
            query += f" AND updated_at >= ${len(params)+1}"
            params.append(filter.updated_after)
        if filter.updated_before:
            query += f" AND updated_at <= ${len(params)+1}"
            params.append(filter.updated_before)

        return query, params