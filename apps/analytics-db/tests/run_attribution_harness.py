"""
ClickHouse attribution harness.

Creates a temporary database, loads the analytics schema, seeds sample
impressions/clicks/events, refreshes the attribution materialized views, and
verifies the expected results. Exits with a non-zero status if any assertion
fails.
"""

from __future__ import annotations

import argparse
import os
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable

import clickhouse_connect
from clickhouse_connect import driver

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DDL_DIR = PROJECT_ROOT / "apps" / "analytics-db" / "create"


TABLE_CREATION_ORDER = [
    "impressions",
    "impressions_queue",
    "impressions_mv",
    "clicks",
    "clicks_queue",
    "clicks_mv",
    "events",
    "events_queue",
    "events_mv",
    "installs_base",
    "installs_base_mv",
    "attributed_impressions",
    "attributed_clicks",
    "attributed_installs",
    "attributed_clicks_mv",
    "attributed_impressions_mv",
    "attributed_installs_mv",
    "user_daily_app_opens",
    "user_daily_app_opens_mv",
    "user_dx_activity",
    "user_dx_activity_mv",
    "user_dx_attributed",
    "user_dx_attributed_mv",
    "user_daily_events",
    "user_daily_events_mv",
    "user_daily_events_attributed",
    "user_daily_events_attributed_mv",
    "daily_overview",
    "daily_overview_mv",
]

REFRESHABLE_VIEWS = [
    "installs_base_mv",
    "attribute_clicks_mv",
    "attribute_impressions_mv",
    "attribute_installs_mv",
    "user_dx_activity_mv",
    "user_dx_attributed_mv",
    "user_daily_events_attributed_mv",
    "daily_overview_mv",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default=os.environ.get("CLICKHOUSE_HOST", "localhost"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("CLICKHOUSE_PORT", "8123")))
    parser.add_argument("--user", default=os.environ.get("CLICKHOUSE_USER", "default"))
    parser.add_argument("--password", default=os.environ.get("CLICKHOUSE_PASSWORD", ""))
    parser.add_argument("--protocol", choices=("http", "https"), default=os.environ.get("CLICKHOUSE_PROTOCOL", "http"))
    parser.add_argument("--database-prefix", default="oa_attr_test", help="Prefix for the temporary database.")
    return parser.parse_args()


def load_schema(client: driver.Client) -> None:
    for name in TABLE_CREATION_ORDER:
        sql_path = DDL_DIR / f"{name}.sql"
        if not sql_path.exists():
            raise FileNotFoundError(f"Expected SQL file missing: {sql_path}")
        sql = sql_path.read_text()
        client.command(sql)


def insert_sample_data(client: driver.Client) -> dict[str, uuid.UUID | datetime | str]:
    store_id = "com.example.superapp"
    network = "meta"
    campaign_name = "winter_campaign"
    campaign_id = "cmp_2025"
    ad_name = "video_variant_a"
    ad_id = "ad_001"
    geo = {"country_iso": "US", "state_iso": "CA", "city_name": "San Francisco"}

    now = datetime.now(timezone.utc).replace(microsecond=0)
    impression_time = now - timedelta(minutes=15)
    click_time = now - timedelta(minutes=10)
    install_time = now - timedelta(minutes=5)
    organic_install_time = now - timedelta(minutes=4)

    ifa_paid = uuid.uuid4()
    oa_paid = uuid.uuid4()
    link_uid = uuid.uuid4()

    ifa_org = uuid.uuid4()
    oa_org = uuid.uuid4()

    client.insert(
        "impressions",
        [
            [
                impression_time,
                store_id,
                network,
                campaign_name,
                campaign_id,
                ad_name,
                ad_id,
                ifa_paid,
                "203.0.113.10",
                geo["country_iso"],
                geo["state_iso"],
                geo["city_name"],
                link_uid,
                impression_time,
            ],
        ],
        column_names=[
            "event_time",
            "store_id",
            "network",
            "campaign_name",
            "campaign_id",
            "ad_name",
            "ad_id",
            "ifa",
            "client_ip",
            "country_iso",
            "state_iso",
            "city_name",
            "link_uid",
            "received_at",
        ],
    )

    client.insert(
        "clicks",
        [
            [
                click_time,
                store_id,
                network,
                campaign_name,
                campaign_id,
                ad_name,
                ad_id,
                ifa_paid,
                "203.0.113.10",
                geo["country_iso"],
                geo["state_iso"],
                geo["city_name"],
                link_uid,
                click_time,
            ],
        ],
        column_names=[
            "event_time",
            "store_id",
            "network",
            "campaign_name",
            "campaign_id",
            "ad_name",
            "ad_id",
            "ifa",
            "client_ip",
            "country_iso",
            "state_iso",
            "city_name",
            "link_uid",
            "received_at",
        ],
    )

    events_rows = [
        [
            install_time,
            store_id,
            "app_open",
            None,
            ifa_paid,
            oa_paid,
            "203.0.113.10",
            geo["country_iso"],
            geo["state_iso"],
            geo["city_name"],
            uuid.uuid4(),
            install_time,
            "",
        ],
        [
            organic_install_time,
            store_id,
            "app_open",
            None,
            ifa_org,
            oa_org,
            "198.51.100.5",
            geo["country_iso"],
            geo["state_iso"],
            geo["city_name"],
            uuid.uuid4(),
            organic_install_time,
            "",
        ],
    ]
    client.insert(
        "events",
        events_rows,
        column_names=[
            "event_time",
            "store_id",
            "event_id",
            "revenue",
            "ifa",
            "oa_uid",
            "client_ip",
            "country_iso",
            "state_iso",
            "city_name",
            "event_uid",
            "received_at",
            "errors",
        ],
    )

    return {
        "store_id": store_id,
        "network": network,
        "campaign_name": campaign_name,
        "ad_name": ad_name,
        "test_date": install_time.date(),
    }


def refresh_views(client: driver.Client) -> None:
    for view in REFRESHABLE_VIEWS:
        client.command(f"ALTER TABLE {view} REFRESH")


def assert_attribution(client: driver.Client, context: dict[str, object]) -> None:
    df = client.query_df(
        """
        SELECT attribution_type, network, count() AS installs
        FROM attributed_installs
        GROUP BY attribution_type, network
        ORDER BY attribution_type
        """
    )
    results = {(row.attribution_type, row.network): row.installs for _, row in df.iterrows()}
    expected = {
        ("click", context["network"]): 1,
        ("Organic", "Organic"): 1,
    }
    if results != expected:
        raise AssertionError(f"Unexpected attribution summary: {results!r} (expected {expected!r})")

    totals = client.query_df("SELECT sum(impressions) AS impressions, sum(clicks) AS clicks, sum(installs) AS installs FROM daily_overview")
    if totals.empty:
        raise AssertionError("daily_overview is empty")
    row = totals.iloc[0]
    if int(row.impressions) != 1 or int(row.clicks) != 1 or int(row.installs) != 2:
        raise AssertionError(f"daily_overview totals mismatch (expected 1/1/2): {row}")


def drop_database(base_client: driver.Client, database: str) -> None:
    base_client.command(f"DROP DATABASE IF EXISTS {database}")


def main() -> int:
    args = parse_args()
    temp_db = f"{args.database_prefix}_{uuid.uuid4().hex[:8]}"

    base_client = clickhouse_connect.get_client(
        host=args.host,
        port=args.port,
        username=args.user,
        password=args.password,
        protocol=args.protocol,
    )
    base_client.command(f"CREATE DATABASE IF NOT EXISTS {temp_db}")

    client = clickhouse_connect.get_client(
        host=args.host,
        port=args.port,
        username=args.user,
        password=args.password,
        protocol=args.protocol,
        database=temp_db,
    )

    try:
        print(f"Loading schema into temporary database '{temp_db}'...")
        load_schema(client)
        print("Inserting sample data...")
        context = insert_sample_data(client)
        print("Refreshing materialized views...")
        refresh_views(client)
        print("Running assertions...")
        assert_attribution(client, context)
        print("All checks passed.")
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"Test harness failed: {exc}", file=sys.stderr)
        return 1
    finally:
        print(f"Dropping temporary database '{temp_db}'...")
        drop_database(base_client, temp_db)


if __name__ == "__main__":
    raise SystemExit(main())
