from __future__ import annotations

from collections.abc import AsyncGenerator
from datetime import datetime, timezone
from pathlib import Path

import httpx
import pytest
import pytest_asyncio

from src.knmi_dataset_downloader import DownloadStats
from src.knmi_dataset_downloader.dataset import DownloadContext, initialize_client

from tests.integration.api_helpers import RunKnmiApiCall, run_or_skip_on_429
from tests.integration.harness import CliDownloadSession, KnmiDownloaderSession


@pytest.fixture
def run_knmi_call() -> RunKnmiApiCall[None]:
    """Inject KNMI API calls with 429 → skip behavior (hourly cooldown)."""
    return run_or_skip_on_429


@pytest.fixture
def knmi_sample_window_short() -> tuple[datetime, datetime]:
    """Fixed historical window with known data (30 minutes on 2024-01-01)."""
    return datetime(2024, 1, 1, 0, 0, 0), datetime(2024, 1, 1, 0, 30, 0)


@pytest.fixture
def knmi_sample_window_day() -> tuple[datetime, datetime]:
    """Full calendar day for limit/slicing tests."""
    return datetime(2024, 1, 1, 0, 0, 0), datetime(2024, 1, 1, 23, 59, 59)


@pytest.fixture
def cli_patched_default_range() -> tuple[datetime, datetime]:
    """UTC range substituted for CLI default-date resolution (stable, has data)."""
    return (
        datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        datetime(2024, 1, 1, 0, 30, 0, tzinfo=timezone.utc),
    )


@pytest_asyncio.fixture
async def cli_download_session(
    tmp_path: Path,
    anonymous_api_key: str,
) -> CliDownloadSession:
    out = tmp_path / "cli_out"
    out.mkdir()
    return CliDownloadSession(api_key=anonymous_api_key, output_dir=out)


@pytest_asyncio.fixture
async def knmi_downloader_session(
    tmp_path: Path,
    anonymous_api_key: str,
) -> AsyncGenerator[KnmiDownloaderSession]:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    client = initialize_client(anonymous_api_key)
    http_client = httpx.AsyncClient()
    context = DownloadContext(
        client=client,
        http_client=http_client,
        dataset_name="Actuele10mindataKNMIstations",
        version="2",
        output_dir=data_dir,
        stats=DownloadStats(),
    )
    yield KnmiDownloaderSession(api_key=anonymous_api_key, context=context)
    await http_client.aclose()
