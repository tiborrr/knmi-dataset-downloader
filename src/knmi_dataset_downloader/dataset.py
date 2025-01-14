from __future__ import annotations

import asyncio
from typing import List, NamedTuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import aiofiles
import httpx
from tqdm.asyncio import tqdm
from kiota_abstractions.authentication.api_key_authentication_provider import (
    ApiKeyAuthenticationProvider,
    KeyLocation,
)
from kiota_http.httpx_request_adapter import HttpxRequestAdapter
from kiota_serialization_json.json_serialization_writer_factory import (
    JsonSerializationWriterFactory,
)
from kiota_serialization_json.json_parse_node_factory import JsonParseNodeFactory

from .knmi_dataset_api.api_client import ApiClient
from .knmi_dataset_api.v1.datasets.item.versions.item.files.files_request_builder import (
    FilesRequestBuilder,
)
from .knmi_dataset_api.v1.datasets.item.versions.item.files.get_order_by_query_parameter_type import (
    GetOrderByQueryParameterType,
)
from .knmi_dataset_api.v1.datasets.item.versions.item.files.get_sorting_query_parameter_type import (
    GetSortingQueryParameterType,
)
from .defaults import (
    DEFAULT_OUTPUT_DIR,
    DEFAULT_DATASET_NAME,
    DEFAULT_DATASET_VERSION,
    DEFAULT_MAX_CONCURRENT,
    get_default_date_range,
)
from .api_key import get_anonymous_api_key

import logging
log = logging.getLogger(__name__)

@dataclass
class DownloadStats:
    """Statistics for the download process."""
    total_files: int = 0
    skipped_files: int = 0
    downloaded_files: int = 0
    failed_files: List[str] = field(default_factory=list)
    total_bytes_downloaded: int = 0

class DownloadContext(NamedTuple):
    """Context for download operations."""
    client: ApiClient
    http_client: httpx.AsyncClient
    semaphore: asyncio.Semaphore
    dataset_name: str
    version: str
    output_dir: Path
    stats: DownloadStats

def initialize_client(api_key: str) -> ApiClient:
    """Initialize the KNMI API client with proper authentication and serialization.

    Args:
        api_key (str): The API key for authentication

    Returns:
        ApiClient: Configured API client
    """
    auth_provider = ApiKeyAuthenticationProvider(
        api_key=api_key,
        parameter_name="Authorization",
        key_location=KeyLocation.Header,
    )

    request_adapter = HttpxRequestAdapter(
        authentication_provider=auth_provider,
        parse_node_factory=JsonParseNodeFactory(),
        serialization_writer_factory=JsonSerializationWriterFactory(),
        base_url="https://api.dataplatform.knmi.nl/open-data",
    )

    return ApiClient(request_adapter)

def format_size(size_bytes: int) -> str:
    """Format bytes into human readable string."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes = int(size_bytes / 1024)
    return f"{size_bytes:.1f} TB"

async def get_files_list(
    context: DownloadContext,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    limit: int | None = None,
) -> List:
    """Get list of files for the specified date range.

    Args:
        context (DownloadContext): Download context containing client and configuration
        start_date (datetime | None): Start date for the files. Defaults to 1 day ago.
        end_date (datetime | None): End date for the files. Defaults to now.
        limit (int | None): Maximum number of files to retrieve. Defaults to None.

    Returns:
        List[FileInfo]: List of file information objects from the KNMI API
    """
    # Use default date range if not specified
    if start_date is None or end_date is None:
        default_start, default_end = get_default_date_range()
        start_date = start_date or default_start
        end_date = end_date or default_end

    if isinstance(start_date, datetime):
        begin = start_date.strftime("%Y-%m-%dT%H:%M:%S+00:00")
    else:
        begin = None

    if isinstance(end_date, datetime):
        end = end_date.strftime("%Y-%m-%dT%H:%M:%S+00:00")
    else:
        end = None

    config = FilesRequestBuilder.FilesRequestBuilderGetQueryParameters(
        max_keys=limit,
        order_by=GetOrderByQueryParameterType.LastModified,
        sorting=GetSortingQueryParameterType.Desc,
        begin=begin,
        end=end,
    )

    request_configuration = FilesRequestBuilder.FilesRequestBuilderGetRequestConfiguration(
        query_parameters=config
    )

    response = await (
        context.client.v1.datasets.by_dataset_name(context.dataset_name)
        .versions.by_version_id(context.version)
        .files.get(request_configuration=request_configuration)
    )

    if response is None:
        raise ValueError("No response from API")

    all_files = response.files or []

    # Handle pagination if there are more files
    while response.is_truncated:
        config.next_page_token = response.next_page_token
        response = await (
            context.client.v1.datasets.by_dataset_name(context.dataset_name)
            .versions.by_version_id(context.version)
            .files.get(request_configuration=request_configuration)
        )
        if response is None:
            raise ValueError("No response from API")
        all_files.extend(response.files or [])
        if limit is not None and len(all_files) >= limit:
            break

    return all_files[:limit]

async def download_file(context: DownloadContext, filename: str, main_progress: tqdm) -> None:
    """Download a single file from the dataset.

    Args:
        context (DownloadContext): Download context containing clients and configuration
        filename (str): Name of the file to download
        main_progress (tqdm): Main progress bar for overall progress
    """
    async with context.semaphore:  # Limit concurrent downloads
        output_path = context.output_dir / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
        
        if output_path.exists():
            context.stats.skipped_files += 1
            main_progress.update(1)
            return

        try:
            download_url = await (
                context.client.v1.datasets.by_dataset_name(context.dataset_name)
                .versions.by_version_id(context.version)
                .files.by_filename(filename=filename)
                .url.get()
            )

            if download_url is None or download_url.temporary_download_url is None:
                raise ValueError("No download URL found")

            # Get file size with a HEAD request
            async with context.http_client.stream(
                "HEAD", download_url.temporary_download_url
            ) as response:
                total_size = int(response.headers.get("content-length", 0))

            # Create progress bar for this file
            file_progress = tqdm(
                total=total_size,
                unit="iB",
                unit_scale=True,
                desc=f"Downloading {filename}",
                leave=False,
            )

            # Stream the download with progress
            async with context.http_client.stream(
                "GET", download_url.temporary_download_url
            ) as response:
                response.raise_for_status()
                async with aiofiles.open(output_path, mode="wb") as f:
                    downloaded_size = 0
                    async for chunk in response.aiter_bytes(chunk_size=8192):
                        await f.write(chunk)
                        chunk_size = len(chunk)
                        downloaded_size += chunk_size
                        file_progress.update(chunk_size)

            file_progress.close()
            main_progress.update(1)

            context.stats.downloaded_files += 1
            context.stats.total_bytes_downloaded += downloaded_size
            log.debug(f"Successfully downloaded: {filename} ({downloaded_size / 1024 / 1024:.1f} MB)")

        except Exception as e:
            log.error(f"Error downloading {filename}: {str(e)}")
            context.stats.failed_files.append(filename)
            if output_path.exists():
                output_path.unlink()  # Remove partially downloaded file
            raise

async def download(
    api_key: str | None = None,
    dataset_name: str = DEFAULT_DATASET_NAME,
    version: str = DEFAULT_DATASET_VERSION,
    max_concurrent: int = DEFAULT_MAX_CONCURRENT,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    limit: int | None = None,
) -> DownloadStats:
    """Download dataset files for the specified date range.

    Args:
        api_key (str | None): KNMI API key. If None, an anonymous API key is used.
        dataset_name (str): Name of the dataset.
        version (str): Version of the dataset.
        max_concurrent (int): Maximum number of concurrent downloads.
        output_dir (str | Path): Output directory for downloaded files.
        start_date (datetime | None): Start date for files to download. Defaults to 1 hour and 30 minutes ago.
        end_date (datetime | None): End date for files to download. Defaults to now.
        limit (int | None): Maximum number of files to download. If None, downloads all files.

    Returns:
        DownloadStats: Statistics about the download process
    """
    if not api_key:
        api_key = await get_anonymous_api_key()

    # Initialize clients and context
    client = initialize_client(api_key)
    http_client = httpx.AsyncClient()
    stats = DownloadStats()
    
    context = DownloadContext(
        client=client,
        http_client=http_client,
        semaphore=asyncio.Semaphore(max_concurrent),
        dataset_name=dataset_name,
        version=version,
        output_dir=Path(output_dir),
        stats=stats
    )

    try:
        files = await get_files_list(context, start_date, end_date, limit)
            
        context.stats.total_files = len(files)
        log.info(f"Found {len(files)} files in date range {start_date} to {end_date}")

        # Main progress bar for overall progress
        with tqdm(
            total=len(files), desc="Overall Progress", unit="file"
        ) as main_progress:
            # Download files concurrently with semaphore limiting
            tasks = [
                download_file(context, file.filename, main_progress) for file in files
            ]
            await asyncio.gather(*tasks, return_exceptions=True)

        # Print summary
        # fmt: off
        log.info("\nDownload Summary:")
        log.info(f"Total files found:     {context.stats.total_files}")
        log.info(f"Files already present: {context.stats.skipped_files}")
        log.info(f"Files downloaded:      {context.stats.downloaded_files}")
        log.info(f"Failed downloads:      {len(context.stats.failed_files)}")
        log.info(f"Total data downloaded: {format_size(context.stats.total_bytes_downloaded)}")
        # fmt: on
        
        if context.stats.failed_files:
            log.warning("\nFailed downloads:")
            for filename in context.stats.failed_files:
                log.warning(f"- {filename}")

    except Exception as e:
        log.error(f"Error during download process: {str(e)}")
        raise

    finally:
        await http_client.aclose()  # Ensure HTTP client is properly closed

    return context.stats
