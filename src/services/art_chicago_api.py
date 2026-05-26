import json
from datetime import datetime, timedelta
from pathlib import Path

import httpx
from sqlalchemy import Boolean

API_URL = "https://api.artic.edu/api/v1"
CACHE_FILE = Path("cache.json")
CACHE_TTL_HOURS = 48

def _check_cache(artwork_id: int) -> tuple[bool, dict | None]:
    """Checks if artwork was checked in last CACHE_TTL_HOURS"""
    if not CACHE_FILE.exists():
        return False, None

    with CACHE_FILE.open("r", encoding="utf-8") as f:
        cache = json.load(f)

    entry = cache.get(str(artwork_id))
    if entry is None:
        return False, None

    cached_at = datetime.fromisoformat(entry["timestamp"])
    if datetime.now() - cached_at > timedelta(hours=CACHE_TTL_HOURS):
        return False, None

    if entry["title"] is None:
        return True, None

    return True, {"id": artwork_id, "title": entry["title"]}


def _save_cache(artwork_id: int, title: str | None) -> bool:
    """Saves cached artwork to cache.json"""
    cache = {}
    if CACHE_FILE.exists():
        with CACHE_FILE.open("r", encoding="utf-8") as f:
            cache = json.load(f)

    cache[str(artwork_id)] = {"title": title, "timestamp": datetime.now().isoformat()}

    with CACHE_FILE.open("w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

    return True


async def fetch_artwork(artwork_id: int) -> dict | None:
    """
    Function returns information about an artwork based on unique ID
    :param artwork_id: external ID of the artwork
    """
    hit, data = _check_cache(artwork_id)
    if hit:
        return data

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            f"{API_URL}/artworks/{artwork_id}",
            params={"fields": "id,title"},
        )

    if response.status_code == 404:
        _save_cache(artwork_id, None)
        return None

    response.raise_for_status()
    data = response.json()["data"]
    _save_cache(artwork_id, data["title"])

    return data

async def validate_and_fetch(artwork_id: int) -> dict:
    """
    Валидирует существование картины в Art Institute API и возвращает её данные.

    Args:
        artwork_id: ID картины в Art Institute API.

    Returns:
        Словарь с полями id и title.

    Raises:
        ValueError: если картина с данным ID не найдена.
        httpx.HTTPStatusError: если API вернул 5xx или другую неожиданную ошибку.
    """
    artwork = await fetch_artwork(artwork_id)
    if artwork is None:
        raise ValueError(f"Artwork {artwork_id} not found in Art Institute API")
    return artwork