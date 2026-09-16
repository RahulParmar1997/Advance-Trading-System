from __future__ import annotations

import pytest

from advance_system.storage.migrations import Migration, MigrationRunner


class FakeConnection:
    def __init__(self, applied: list[int], fail_on: str | None = None) -> None:
        self.applied = applied
        self.fail_on = fail_on
        self.closed = False
        self.calls: list[tuple[str, tuple[object, ...]]] = []

    async def execute(self, statement: str, *parameters: object) -> object:
        self.calls.append((statement, parameters))
        if statement == self.fail_on:
            raise RuntimeError("migration failed")
        if statement.startswith("SELECT version"):
            return [(version,) for version in self.applied]
        if statement.startswith("INSERT INTO schema_migrations"):
            self.applied.append(int(parameters[0]))
        return None

    async def close(self) -> None:
        self.closed = True


@pytest.mark.asyncio
async def test_runner_applies_only_pending_migrations() -> None:
    connection = FakeConnection([1])

    async def factory() -> FakeConnection:
        return connection

    runner = MigrationRunner(factory)
    migrations = [Migration(2, "second", "CREATE TABLE second_table (id INTEGER)"), Migration(1, "first", "CREATE TABLE first_table (id INTEGER)")]

    assert await runner.run(migrations) == (2,)
    assert connection.applied == [1, 2]
    assert connection.closed is True


@pytest.mark.asyncio
async def test_runner_is_idempotent() -> None:
    connection = FakeConnection([1, 2])

    async def factory() -> FakeConnection:
        return connection

    runner = MigrationRunner(factory)
    migrations = [Migration(1, "first", "SELECT 1"), Migration(2, "second", "SELECT 2")]

    assert await runner.run(migrations) == ()
    assert not any("INSERT INTO schema_migrations" in call[0] for call in connection.calls)
    assert connection.closed is True


@pytest.mark.asyncio
async def test_runner_closes_connection_when_migration_fails() -> None:
    connection = FakeConnection([], fail_on="CREATE TABLE broken_table (id INTEGER)")

    async def factory() -> FakeConnection:
        return connection

    runner = MigrationRunner(factory)

    with pytest.raises(RuntimeError, match="migration failed"):
        await runner.run((Migration(1, "broken", "CREATE TABLE broken_table (id INTEGER)"),))

    assert connection.closed is True


def test_runner_rejects_duplicate_versions() -> None:
    with pytest.raises(ValueError, match="duplicate"):
        MigrationRunner(lambda: None)._validate_migrations((Migration(1, "a", "SELECT 1"), Migration(1, "b", "SELECT 2")))
