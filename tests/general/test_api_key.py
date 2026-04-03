from __future__ import annotations


async def test_anonymous_api_key_fetch(anonymous_api_key: str) -> None:
    """Fetch anonymous API key from KNMI developer portal (real HTTP)."""
    assert isinstance(anonymous_api_key, str)
    assert len(anonymous_api_key) > 0
    assert anonymous_api_key.startswith("eyJ")
    allowed = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-")
    assert all(c in allowed for c in anonymous_api_key)
