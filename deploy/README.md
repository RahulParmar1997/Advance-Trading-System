# Deployment and Operations

## Safety posture

The deployment stack is PAPER-first. Do not add broker credentials to Compose files, images, logs, or source control. Live execution remains behind the application RiskEngine → OMS path and is not enabled by infrastructure alone.

## Local deployment

1. Create a secret-bearing environment outside git and provide `POSTGRES_PASSWORD`.
2. Start the stack with `docker compose up -d --build`.
3. Verify dependency health with `docker compose ps`.
4. Access the terminal through the reverse proxy on port `8080` when the proxy service is enabled in the production profile.
5. Stop with `docker compose down`; retain named volumes when data preservation is required.

## Health signals

- PostgreSQL: `pg_isready` health check.
- ClickHouse: `/ping` health check.
- Redis: `redis-cli ping` health check.
- Reverse proxy: `GET /healthz`.
- Backend application health/readiness checks must remain fail-closed.

## Operational alerts

Treat these as high priority:

- PostgreSQL unavailable or repeated connection failures.
- Market-data freshness outside configured thresholds.
- Broker connectivity/status degraded.
- RiskEngine kill switch or circuit breaker engaged.
- OMS reconciliation mismatch.
- Journal integrity failure.
- Unexpected transition toward LIVE mode.

Never silence an execution-safety alert to restore apparent availability.

## Incident procedure

1. Preserve evidence: logs, health state, journal/checkpoint state, and timestamps.
2. If execution safety is uncertain, activate the application kill switch and stop new order admission.
3. Do not repair operational state by editing Redis, ClickHouse, Parquet, or journal files manually.
4. Reconcile PostgreSQL operational state with authoritative broker responses before resuming.
5. Resume only after data freshness, broker status, risk controls, and reconciliation are healthy.

## Reverse proxy

`nginx/nginx.conf` exposes only the frontend through the proxy and provides security headers plus a non-authenticated health endpoint. It does not proxy a broker API or provide an execution endpoint.

## Monitoring

`prometheus/prometheus.yml` is a deployment template. The backend target is intentionally explicit and should only be enabled when the backend exposes `/metrics`. Monitoring must observe the system; it must never become an execution control plane.
