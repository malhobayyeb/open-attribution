"""Service health checks."""

from __future__ import annotations

from typing import Self

from dbcon import queries
from litestar import Controller, get
from sqlalchemy import text

from dash_api.controllers.analytics import client as clickhouse_client


class HealthController(Controller):
    """Expose basic health and dependency checks."""

    path = "/health"

    @get(path="/")
    async def health(self: Self) -> dict:
        """Return statuses for Postgres and ClickHouse dependencies."""
        checks = {
            "postgres": self._check_postgres(),
            "clickhouse": self._check_clickhouse(),
        }
        overall = all(result["healthy"] for result in checks.values())
        return {"status": "ok" if overall else "degraded", "checks": checks}

    @staticmethod
    def _check_postgres() -> dict[str, str | bool]:
        try:
            with queries.ENGINE.connect() as conn:
                conn.execute(text("SELECT 1"))
            return {"healthy": True, "detail": "ok"}
        except Exception as exc:  # noqa: BLE001
            return {"healthy": False, "detail": str(exc)}

    @staticmethod
    def _check_clickhouse() -> dict[str, str | bool]:
        try:
            clickhouse_client.command("SELECT 1")
            return {"healthy": True, "detail": "ok"}
        except Exception as exc:  # noqa: BLE001
            return {"healthy": False, "detail": str(exc)}
