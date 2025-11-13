"""Trigger cache refreshes in the postback API."""

from __future__ import annotations

import requests

from config import POSTBACK_API_URL, get_logger

logger = get_logger(__name__)

BASE_URL = POSTBACK_API_URL.rstrip("/")

DEFAULT_TIMEOUT = 5


def _post(path: str, description: str) -> None:
    url = f"{BASE_URL}{path}"
    try:
        response = requests.post(url, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
        logger.info("Triggered %s cache refresh via %s", description, url)
    except requests.RequestException as exc:  # noqa: BLE001
        # Avoid failing the user-facing request: log and move on.
        logger.warning("Failed to refresh %s cache via %s: %s", description, url, exc)


def refresh_app_links_cache() -> None:
    """Refresh the share link cache inside the postback API."""
    _post("/api/links/update", "app link")


def refresh_apps_cache() -> None:
    """Refresh the app metadata cache used for well-known responses."""
    _post("/.well-known/updateapps", "app metadata")
