from __future__ import annotations

import pytest

from advance_system.storage.migrations import Migration, MigrationRunner


class FakeConnection:
    def __init__(self, applied: list[int]) -> None:
        self.applied = applied
        self.calls: list[tuple[str, tuple[object, ...]]] = []

    async def execute(self, statement: str, *parameters: object) -> object:
        self.calls.append((statement, parameters))
        if statement.startswith("SELECT version"):
            return [(version,) for version in self.applied]
        if statement.startswith("INSERT INTO schema_migrations"):
            self.applied.append(int(parameters[0]))
        return None


@pytest.mark.asyncio
async def test_runner_applies_only_pending_migrations() -> None:
    connection = FakeConnection([1])

    async def factory() -> FakeConnection:
        return connection

    runner = MigrationRunner(factory)
    migrations = [Migration(2, "second", "CREATE TABLE second_table (id INTEGER)"), Migration(1, "first", "CREATE TABLE first_table (id INTEGER)")]

    assert await runner.run(migrations) == (2,)
    assert connection.applied == [1, 2]


@pytest.mark.asyncio
async def test_runner_is_idempotent() -> None:
    connection = FakeConnection([1, 2])

    async def factory() -> FakeConnection:
        return connection

    runner = MigrationRunner(factory)
    migrations = [Migration(1, "first", "SELECT 1"), Migration(2, "second", "SELECT 2")]

    assert await runner.run(migrations) == ()
    assert not any("INSERT INTO schema_migrations" in call[0] for call in connection.calls)


def test_runner_rejects_duplicate_versions() -> None:
    with pytest.raises(ValueError, match="duplicate"):
        MigrationRunner(lambda: None)._validate_migrations((Migration(1, "a", "SELECT 1"), Migration(1, "b", "SELECT 2")))
