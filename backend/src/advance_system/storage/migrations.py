from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Sequence


class MigrationConnection(Protocol):
    async def execute(self, statement: str, *parameters: object) -> object: ...


class MigrationConnectionFactory(Protocol):
    async def __call__(self) -> MigrationConnection: ...


@dataclass(frozen=True, slots=True)
class Migration:
    version: int
    name: str
    sql: str

    def validate(self) -> None:
        if self.version <= 0:
            raise ValueError("migration version must be positive")
        if not self.name.strip():
            raise ValueError("migration name is required")
        if not self.sql.strip():
            raise ValueError("migration SQL is required")


class MigrationRunner:
    """Idempotent migration runner using PostgreSQL as migration-state authority."""

    TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS schema_migrations (
        version INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        applied_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    """

    def __init__(self, connection_factory: MigrationConnectionFactory) -> None:
        self._connection_factory = connection_factory

    async def run(self, migrations: Sequence[Migration]) -> tuple[int, ...]:
        ordered = tuple(sorted(migrations, key=lambda migration: migration.version))
        self._validate_migrations(ordered)
        connection = await self._connection_factory()
        await connection.execute(self.TABLE_SQL)
        applied = await self._applied_versions(connection)
        executed: list[int] = []
        for migration in ordered:
            if migration.version in applied:
                continue
            await connection.execute(migration.sql)
            await connection.execute(
                "INSERT INTO schema_migrations (version, name) VALUES ($1, $2)",
                migration.version,
                migration.name,
            )
            executed.append(migration.version)
        return tuple(executed)

    async def _applied_versions(self, connection: MigrationConnection) -> set[int]:
        result = await connection.execute("SELECT version FROM schema_migrations ORDER BY version")
        rows = result if isinstance(result, Sequence) and not isinstance(result, (str, bytes)) else ()
        versions: set[int] = set()
        for row in rows:
            if isinstance(row, int):
                versions.add(row)
            elif isinstance(row, Sequence) and row and isinstance(row[0], int):
                versions.add(row[0])
            elif isinstance(row, dict) and isinstance(row.get("version"), int):
                versions.add(row["version"])
            else:
                raise ValueError("invalid schema_migrations row")
        return versions

    @staticmethod
    def _validate_migrations(migrations: Sequence[Migration]) -> None:
        seen: set[int] = set()
        for migration in migrations:
            migration.validate()
            if migration.version in seen:
                raise ValueError(f"duplicate migration version: {migration.version}")
            seen.add(migration.version)
