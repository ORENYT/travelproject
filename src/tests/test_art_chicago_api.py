import json
import pytest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from src.services.art_chicago_api import fetch_artwork

TEST_CACHE_FILE = Path("test_cache.json")


@pytest.fixture(autouse=True)
def clean_cache(monkeypatch):
    monkeypatch.setattr("src.services.art_chicago_api.CACHE_FILE", TEST_CACHE_FILE)
    yield
    TEST_CACHE_FILE.unlink(missing_ok=True)


def write_cache(artwork_id: int, title: str | None, hours_ago: float = 0):
    timestamp = (datetime.now() - timedelta(hours=hours_ago)).isoformat()
    TEST_CACHE_FILE.write_text(json.dumps({
        str(artwork_id): {"title": title, "timestamp": timestamp}
    }))


@pytest.mark.asyncio
async def test_cache_hit_returns_without_api_call():
    write_cache(123, "Mona Lisa")

    with patch("src.services.art_chicago_api.httpx.AsyncClient") as mock_client:
        result = await fetch_artwork(123)

    assert result == {"id": 123, "title": "Mona Lisa"}
    mock_client.assert_not_called()


@pytest.mark.asyncio
async def test_cache_expired_calls_api():
    write_cache(123, "Mona Lisa", hours_ago=49)

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": {"id": 123, "title": "Mona Lisa Updated"}}

    with patch("src.services.art_chicago_api.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
        result = await fetch_artwork(123)

    assert result["title"] == "Mona Lisa Updated"


@pytest.mark.asyncio
async def test_cache_stores_none_for_missing_artwork():
    mock_response = MagicMock()
    mock_response.status_code = 404

    with patch("src.services.art_chicago_api.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
        result = await fetch_artwork(99999)

    assert result is None
    cache = json.loads(TEST_CACHE_FILE.read_text())
    assert cache["99999"]["title"] is None


@pytest.mark.asyncio
async def test_real_api_call():
    result = await fetch_artwork(27992)
    assert result is not None
    assert result["id"] == 27992
    assert "Grande Jatte" in result["title"]