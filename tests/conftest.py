from __future__ import annotations

import pytest_asyncio

from src.knmi_dataset_downloader.api_key import get_anonymous_api_key


@pytest_asyncio.fixture
async def anonymous_api_key() -> str:
    return await get_anonymous_api_key()
