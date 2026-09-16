from __future__ import annotations

import pytest

from advance_system.storage.migrations import Migration, MigrationRunner


class FakeTransaction:
    def __init__(self, connection: "FakeConnection") -> None:
        self.connection = connection
        self._applied_snapshot: list[int] = []

    async def __aenter__(self) -> "FakeTransaction":
        self.connection.transaction_started = True
        self._applied_snapshot = list(self.connection.applied)
        return self

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> bool:
        self.connection.transaction_committed = exc_type is None
        self.connection.transaction_rolled_back = exc_type is not None
        if exc_type is not None:
            self.connection.applied[:] = self._applied_snapshot
        return False


class FakeConnection:
    def __init__(self, applied: list[int], fail_on: str | None = None) -> None:
        self.applied = applied
        self.fail_on = fail_on
        self.closed = False
        self.transaction_started = False
        self.transaction_committed = False
        self.transaction_rolled_back = False
        self.calls: list[tuple[str, tuple[object, ...]]] = []

    def transaction(self) -> FakeTransaction:
        return FakeTransaction(self)

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
async def test_runner_applies_only_pending_migrations_atomically() -> None:
    connection = FakeConnection([1])

    async def factory() -> FakeConnection:
        return connection

    runner = MigrationRunner(factory)
    migrations = [Migration(2, "second", "CREATE TABLE second_table (id INTEGER)"), Migration(1, "first", "CREATE TABLE first_table (id INTEGER)")]

    assert await runner.run(migrations) == (2,)
    assert connection.applied == [1, 2]
    assert connection.transaction_started is True
    assert connection.transaction_committed is True
    assert connection.transaction_rolled_back is False
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
    assert connection.transaction_committed is True
    assert connection.closed is True


@pytest.mark.asyncio
async def test_runner_rolls_back_partial_migrations_and_closes_connection() -> None:
    connection = FakeConnection([], fail_on="CREATE TABLE broken_table (id INTEGER)")

    async def factory() -> FakeConnection:
        return connection

    runner = MigrationRunner(factory)
    migrations = (
        Migration(1, "first", "CREATE TABLE first_table (id INTEGER)"),
        Migration(2, "broken", "CREATE TABLE broken_table (id INTEGER)"),
    )

    with pytest.raises(RuntimeError, match="migration failed"):
        await runner.run(migrations)

    assert connection.applied == []
    assert connection.transaction_started is True
    assert connection.transaction_committed is False
    assert connection.transaction_rolled_back is True
    assert connection.closed is True


def test_runner_rejects_duplicate_versions() -> None:
    with pytest.raises(ValueError, match="duplicate"):
        MigrationRunner(lambda: None)._validate_migrations((Migration(1, "a", "SELECT 1"), Migration(1, "b", "SELECT 2")))
