from __future__ import annotations

from datetime import datetime
from unittest.mock import patch

from src.knmi_dataset_downloader.cli import async_main
from tests.integration.api_helpers import RunKnmiApiCall
from tests.integration.harness import CliDownloadSession


async def test_cli_with_real_api(
    cli_download_session: CliDownloadSession,
    run_knmi_call: RunKnmiApiCall[None],
) -> None:
    s = cli_download_session
    test_args = [
        "--api-key",
        s.api_key,
        "--start-date",
        "2024-01-01T00:00:00",
        "--end-date",
        "2024-01-01T00:20:00",
        "--concurrent",
        "2",
        "--output-dir",
        str(s.output_dir),
        "--limit",
        "1",
    ]

    async def run_cli() -> None:
        with patch("sys.argv", ["knmi-download", *test_args]):
            await async_main()

    await run_knmi_call(run_cli)

    nc_files = list(s.output_dir.glob("*.nc"))
    assert len(nc_files) <= 1, "More than one file was downloaded despite limit=1"
    assert len(nc_files) > 0, "No .nc files were downloaded"


async def test_cli_with_defaults(
    cli_download_session: CliDownloadSession,
    run_knmi_call: RunKnmiApiCall[None],
    cli_patched_default_range: tuple[datetime, datetime],
) -> None:
    s = cli_download_session
    test_args = [
        "--output-dir",
        str(s.output_dir),
        "--limit",
        "1",
    ]

    async def run_cli() -> None:
        with (
            patch(
                "src.knmi_dataset_downloader.cli.get_default_date_range",
                return_value=cli_patched_default_range,
            ),
            patch("sys.argv", ["knmi-download", *test_args]),
        ):
            await async_main()

    await run_knmi_call(run_cli)

    nc_files = list(s.output_dir.glob("*.nc"))
    assert len(nc_files) <= 1, "More than one file was downloaded despite limit=1"
    assert len(nc_files) > 0, "No .nc files were downloaded with default date range"
