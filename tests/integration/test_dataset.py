from __future__ import annotations

from datetime import datetime

from src.knmi_dataset_downloader import download, DownloadStats
from src.knmi_dataset_downloader.dataset import get_files_list

from tests.integration.api_helpers import RunKnmiApiCall
from tests.integration.harness import KnmiDownloaderSession


def test_download_stats() -> None:
    stats = DownloadStats()
    assert stats.total_files == 0
    assert stats.skipped_files == 0
    assert stats.downloaded_files == 0
    assert stats.failed_files == []
    assert stats.total_bytes_downloaded == 0


async def test_api_size_matches_file_size(
    knmi_downloader_session: KnmiDownloaderSession,
    run_knmi_call: RunKnmiApiCall[None],
    knmi_sample_window_short: tuple[datetime, datetime],
) -> None:
    s = knmi_downloader_session
    start_date, end_date = knmi_sample_window_short

    async def run() -> None:
        files = await get_files_list(
            context=s.context,
            start_date=start_date,
            end_date=end_date,
            limit=1,
        )
        assert len(files) > 0, "No files found in the test period"
        test_file = files[0]
        assert test_file.size is not None, "API did not return a file size"
        api_size = test_file.size

        _: DownloadStats = await download(
            api_key=s.api_key,
            output_dir=s.output_dir,
            start_date=start_date,
            end_date=end_date,
            limit=1,
        )

        downloaded_files = [p for p in s.output_dir.rglob("*") if p.is_file()]
        assert len(downloaded_files) == 1, "Expected exactly one downloaded file"
        downloaded_file = downloaded_files[0]
        assert downloaded_file.stat().st_size == api_size, (
            f"API reported size ({api_size} bytes) does not match actual file size"
        )

    await run_knmi_call(run)


async def test_download(
    knmi_downloader_session: KnmiDownloaderSession,
    run_knmi_call: RunKnmiApiCall[None],
    knmi_sample_window_short: tuple[datetime, datetime],
) -> None:
    s = knmi_downloader_session
    start_date, end_date = knmi_sample_window_short

    async def run() -> None:
        stats = await download(
            api_key=s.api_key,
            output_dir=s.output_dir,
            start_date=start_date,
            end_date=end_date,
            limit=1,
        )
        assert stats.total_files == 1, "Should only download 1 file"
        assert stats.downloaded_files + stats.skipped_files <= 1
        assert len(stats.failed_files) == 0, "No files should fail"

    await run_knmi_call(run)


async def test_download_with_limit(
    knmi_downloader_session: KnmiDownloaderSession,
    run_knmi_call: RunKnmiApiCall[None],
    knmi_sample_window_day: tuple[datetime, datetime],
) -> None:
    s = knmi_downloader_session
    start_date, end_date = knmi_sample_window_day

    async def run() -> None:
        for limit in (1, 2):
            stats = await download(
                api_key=s.api_key,
                output_dir=s.output_dir,
                start_date=start_date,
                end_date=end_date,
                limit=limit,
            )
            assert stats.total_files == limit, f"Should limit to {limit} files"
            assert stats.downloaded_files + stats.skipped_files <= limit, (
                f"Total processed files should not exceed limit of {limit}"
            )

    await run_knmi_call(run)
