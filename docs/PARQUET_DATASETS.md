# Parquet / Object-Storage Research Datasets

Parquet/object storage is the immutable research-data layer. It is **not** an execution authority and must never replace PostgreSQL operational truth.

## Layout

Each dataset is addressed by an explicit dataset name, version, and partition:

```text
<root>/dataset=<dataset>/version=<version>/partition=<partition>/data.parquet
<root>/dataset=<dataset>/version=<version>/partition=<partition>/manifest.json
```

The manifest records the SHA-256 content hash, byte size, UTC creation time, and immutable flag.

## Immutability rules

- Dataset, version, and partition identifiers are restricted to safe path components.
- A version is append-only: it cannot be overwritten with different content.
- Re-submitting identical content to an existing version is idempotent.
- The adapter verifies the payload against the manifest on every read.
- The adapter has no delete or overwrite operation.
- The Parquet payload must begin with the Parquet magic bytes (`PAR1`).

## Versioning

Versions are explicit application-owned identifiers such as `v1`, `v2`, or a semantic dataset schema version. A new schema or incompatible research representation must use a new version rather than mutating an existing dataset version.

Partitions are useful for immutable slices such as `date=2026-09-15`, instrument, or other research dimensions. Partition values are part of the immutable dataset address.

## Provider boundary

`ImmutableParquetStore` depends on a minimal injected `ObjectStore` protocol. Cloud-provider SDKs and credentials stay outside the storage domain and can be introduced later without changing dataset semantics.
