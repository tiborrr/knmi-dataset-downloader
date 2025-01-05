from __future__ import annotations

import asyncio
from typing import List
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
@dataclass
class DownloadStats:
    """Statistics for the download process."""

    total_files: int = 0
    skipped_files: int = 0
    downloaded_files: int = 0
    failed_files: List[str] = field(default_factory=list)
    total_bytes_downloaded: int = 0


class Downloader:
    def __init__(
        self,
        api_key: str | None = None,
        dataset_name: str = DEFAULT_DATASET_NAME,
        version: str = DEFAULT_DATASET_VERSION,
        max_concurrent: int = DEFAULT_MAX_CONCURRENT,
        output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    ):
        """Initialize the KNMI Dataset client.

        Args:
            dataset_name (str, optional): Name of the dataset. Defaults to DEFAULT_DATASET_NAME.
            version (str, optional): Version of the dataset. Defaults to DEFAULT_DATASET_VERSION.
            max_concurrent (int, optional): Maximum number of concurrent downloads. Defaults to DEFAULT_MAX_CONCURRENT.
            api_key (str): KNMI API key.
            output_dir (str | Path, optional): Output directory for downloaded files. Defaults to DEFAULT_OUTPUT_DIR.
        """
        if not api_key:
            raise ValueError("API key is required")

        self.dataset_name = dataset_name
        self.version = version
        self.max_concurrent = max_concurrent
        self.api_key = api_key or asyncio.run(get_anonymous_api_key())
        self.output_dir = Path(output_dir)
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.client = self._initialize_client()
        self.http_client = httpx.AsyncClient()
        self.stats = DownloadStats()

    def _initialize_client(self) -> ApiClient:
        """Initialize the KNMI API client with proper authentication and serialization.

        Returns:
            WeatherDataClient: Configured API client
        """
        auth_provider = ApiKeyAuthenticationProvider(
            api_key=self.api_key,
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

    async def _get_files_list(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        max_keys: int = 1000,
    ) -> List:
        """Get list of files for the specified date range.

        Args:
            start_date (datetime): Start date for the files. Defaults to 1 day ago.
            end_date (datetime): End date for the files. Defaults to now.
            max_keys (int, optional): Maximum number of files to retrieve per page. Defaults to 1000.

        Returns:
            List: List of file information
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
            max_keys=max_keys,
            order_by=GetOrderByQueryParameterType.LastModified,
            sorting=GetSortingQueryParameterType.Desc,
            begin=begin,
            end=end,
        )

        request_configuration = (
            FilesRequestBuilder.FilesRequestBuilderGetRequestConfiguration(
                query_parameters=config
            )
        )

        response = await (
            self.client.v1.datasets.by_dataset_name(self.dataset_name)
            .versions.by_version_id(self.version)
            .files.get(request_configuration=request_configuration)
        )

        if response is None:
            raise ValueError("No response from API")

        all_files = response.files or []

        # Handle pagination if there are more files
        while response.is_truncated:
            config.next_page_token = response.next_page_token
            response = await (
                self.client.v1.datasets.by_dataset_name(self.dataset_name)
                .versions.by_version_id(self.version)
                .files.get(request_configuration=request_configuration)
            )
            if response is None:
                raise ValueError("No response from API")
            all_files.extend(response.files or [])

        return all_files

    async def _download_file(self, filename: str, main_progress: tqdm) -> None:
        """Download a single file from the dataset.

        Args:
            filename (str): Name of the file to download
            main_progress (tqdm): Main progress bar for overall progress
        """
        async with self.semaphore:  # Limit concurrent downloads
            output_path = self.output_dir / filename
            output_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
            
            if output_path.exists():
                self.stats.skipped_files += 1
                main_progress.update(1)
                return

            try:
                download_url = await (
                    self.client.v1.datasets.by_dataset_name(self.dataset_name)
                    .versions.by_version_id(self.version)
                    .files.by_filename(filename=filename)
                    .url.get()
                )

                if download_url is None or download_url.temporary_download_url is None:
                    raise ValueError("No download URL found")

                # Get file size with a HEAD request
                async with self.http_client.stream(
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
                async with self.http_client.stream(
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

                self.stats.downloaded_files += 1
                self.stats.total_bytes_downloaded += downloaded_size
                # main_progress.write(f"Successfully downloaded: {filename} ({downloaded_size / 1024 / 1024:.1f} MB)")

            except Exception as e:
                main_progress.write(f"Error downloading {filename}: {str(e)}")
                self.stats.failed_files.append(filename)
                if output_path.exists():
                    output_path.unlink()  # Remove partially downloaded file
                raise

    def _format_size(self, size_bytes: int) -> str:
        """Format bytes into human readable string."""
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes = int(size_bytes / 1024)
        return f"{size_bytes:.1f} TB"

    async def download(
        self, start_date: datetime | None = None, end_date: datetime | None = None
    ) -> None:
        """Download all dataset files for the specified date range.

        Args:
            start_date (datetime): Start date for the files to download. Defaults to 1 day ago.
            end_date (datetime): End date for the files to download. Defaults to now.
        """
        try:
            files = await self._get_files_list(start_date, end_date)
            self.stats.total_files = len(files)
            print(f"Found {len(files)} files in date range {start_date} to {end_date}")

            # Main progress bar for overall progress
            with tqdm(
                total=len(files), desc="Overall Progress", unit="file"
            ) as main_progress:
                # Download files concurrently with semaphore limiting
                tasks = [
                    self._download_file(file.filename, main_progress) for file in files
                ]
                await asyncio.gather(*tasks, return_exceptions=True)

            # Print summary
            print("\nDownload Summary:")
            print(f"Total files found: {self.stats.total_files}")
            print(f"Files already present: {self.stats.skipped_files}")
            print(f"Files downloaded: {self.stats.downloaded_files}")
            print(f"Failed downloads: {len(self.stats.failed_files)}")
            print(
                f"Total data downloaded: {self._format_size(self.stats.total_bytes_downloaded)}"
            )

            if self.stats.failed_files:
                print("\nFailed downloads:")
                for filename in self.stats.failed_files:
                    print(f"- {filename}")

        except Exception as e:
            print(f"Error during download process: {str(e)}")
            raise

        finally:
            await self.http_client.aclose()  # Ensure HTTP client is properly closed
