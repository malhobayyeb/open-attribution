## ClickHouse Attribution Harness

The attribution logic for OpenAttribution lives entirely inside the ClickHouse
materialized views under `apps/analytics-db/create`. This harness lets you
replay a small, deterministic dataset into an isolated ClickHouse database and
assert that the attribution tables and `daily_overview` rollups match the
expected counts. It is intended to be the first step toward the “integration
tests that replay sample datasets” item on the roadmap.

### Prerequisites

- Python environment with the repository’s `pyproject.toml` dependencies
  installed (notably `clickhouse-connect`).
- Access to a ClickHouse server (the local Docker stack works fine). Provide
  credentials via CLI flags or environment variables.

### Usage

```bash
cd apps/analytics-db
python -m tests.run_attribution_harness \
  --host localhost \
  --port 8123 \
  --user "${CLICKHOUSE_USER:-default}" \
  --password "${CLICKHOUSE_PASSWORD:-}" \
  --protocol http
```

Key behaviours:

- A temporary database (named `oa_attr_test_<random>`) is created so the test
  data never pollutes an existing environment.
- Every table/materialized view defined under `apps/analytics-db/create` is
  recreated inside that database using the same order as the Docker startup
  script.
- Synthetic impressions, clicks, and events (including an organic install) are
  inserted directly into the base tables.
- All `REFRESH EVERY …` materialized views are refreshed explicitly so their
  results are immediately available.
- Assertions verify that:
  - Exactly one attributed install is linked to a click (with the configured
    network/campaign), and one install is marked “Organic”.
  - `daily_overview` reports 1 impression, 1 click, and 2 installs in total.
- The temporary database is dropped whether the test passes or fails.

The script exits with non‑zero status (and prints helpful context) if any
assertion fails, making it suitable for future CI integration.
