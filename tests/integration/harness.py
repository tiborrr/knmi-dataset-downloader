from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import httpx

from src.knmi_dataset_downloader.dataset import DownloadContext


@dataclass(frozen=True, slots=True)
class CliDownloadSession:
    """CLI integration: anonymous key and an isolated output directory."""

    api_key: str
    output_dir: Path


@dataclass(frozen=True, slots=True)
class KnmiDownloaderSession:
    """Dataset API integration: Kiota client context and matching credentials."""

    api_key: str
    context: DownloadContext

    @property
    def output_dir(self) -> Path:
        return self.context.output_dir

    @property
    def http_client(self) -> httpx.AsyncClient:
        return self.context.http_client
