# Dashboard Backend

The dashboard backend is a Litestar application that exposes analytics (`/api/overview`)
and metadata CRUD endpoints. It depends on both Postgres (for metadata) and
ClickHouse (for analytics queries), and it now calls the postback API whenever
metadata changes so runtime caches stay fresh.

## Required Environment Variables

| Variable            | Description                                                |
| ------------------- | ---------------------------------------------------------- |
| `POSTGRES_DB`       | Admin database name                                        |
| `POSTGRES_USER`     | Admin database user                                        |
| `POSTGRES_PASSWORD` | Admin database password                                    |
| `CLICKHOUSE_USER`   | ClickHouse username                                        |
| `CLICKHOUSE_PASSWORD` | ClickHouse password                                      |
| `POSTBACK_API_URL`  | Base URL for the postback API (defaults to `http://postback-api:8000`) |

When running the docker-compose stack, these values are provided via `.dev.env`
or `.production.env`. For local development without Docker, export the variables
before starting `litestar run`.
