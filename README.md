# KNMI Dataset Downloader

A Python package for easily downloading datasets from the KNMI (Royal Netherlands Meteorological Institute) Data Platform. This tool supports concurrent downloads and provides both a command-line interface and a Python API.

## Background

This project was inspired by my experience working at Clairify ([https://www.clairify.io](https://www.clairify.io)), where I worked extensively with KNMI datasets. After leaving, I had more time to create this tool to address the need for a more streamlined download process. The goal was to simplify dataset acquisition for Python projects, making it easier for developers and data scientists to work with KNMI's valuable meteorological data.

## Features

- Concurrent downloads for improved performance
- Progress bars for overall and per-file downloads
- Date range filtering (CLI and API translate times to UTC for the KNMI list-files API)
- Skips files that are already present on disk
- CLI and Python `async` API
- Download statistics (`DownloadStats`)
- Anonymous API key: optional automatic fetch from the KNMI developer portal (HTTP client timeout on that request)
- Kiota-generated client for the KNMI Open Data API

## Installation

From [PyPI](https://pypi.org/project/knmi-dataset-downloader/):

```bash
pip install knmi-dataset-downloader
```

**From source** (dependencies are declared in `pyproject.toml`; lockfile is `uv.lock` if you use [uv](https://docs.astral.sh/uv/)):

```bash
git clone https://github.com/tiborrr/knmi-dataset-downloader.git
cd knmi-dataset-downloader
uv sync                  # recommended: creates .venv and installs project + dev tools
# or: pip install .
```

## Prerequisites

- **Python 3.14+** (see `requires-python` in `pyproject.toml`)
- KNMI Data Platform API key **optional** — if you omit `--api-key` / `api_key`, an anonymous key is fetched from the developer portal

## Usage

### Command line

```bash
# With your own API key
knmi-download --api-key YOUR_API_KEY --start-date 2024-01-01T00:00:00 --end-date 2024-01-31T23:59:59

# Anonymous key (fetched for you)
knmi-download --start-date 2024-01-01 --end-date 2024-01-31

# Cap how many files to download
knmi-download --start-date 2024-01-01 --end-date 2024-01-31 --limit 5
```

If you omit `--start-date` / `--end-date`, the CLI defaults to the **last 1 hour 30 minutes in UTC** through **now (UTC)**.

Use `-o` / `--output-dir` to choose where files go (default: `./datasets` relative to the current working directory).

Typical options (see `knmi-download --help` for the full list):

| Option | Description |
|--------|-------------|
| `-d`, `--dataset` | Dataset name (default: `Actuele10mindataKNMIstations`) |
| `-v`, `--version` | Dataset version (default: `2`) |
| `-c`, `--concurrent` | Max concurrent downloads (default: `10`) |
| `-s`, `--start-date` | ISO 8601 start (default: ~1h30 ago UTC) |
| `-e`, `--end-date` | ISO 8601 end (default: now UTC) |
| `--api-key` | KNMI API key (optional) |
| `-o`, `--output-dir` | Output directory (default: `./datasets`) |
| `--limit` | Maximum number of files |

### Python API

```python
import asyncio
from datetime import datetime

from knmi_dataset_downloader import download, DownloadStats


async def main() -> None:
    stats: DownloadStats = await download(
        api_key="YOUR_API_KEY",  # Optional; anonymous key is used if omitted / None
        dataset_name="Actuele10mindataKNMIstations",
        version="2",
        max_concurrent=10,
        output_dir="path/to/output",  # default: ./datasets
        start_date=datetime(2024, 1, 1, 0, 0, 0),
        end_date=datetime(2024, 1, 31, 23, 59, 59),
        limit=5,
    )
    print(f"Total files found: {stats.total_files}")
    print(f"Files downloaded: {stats.downloaded_files}")
    print(f"Files skipped: {stats.skipped_files}")


if __name__ == "__main__":
    asyncio.run(main())
```

Public re-exports also include `DEFAULT_DATASET_NAME`, `DEFAULT_DATASET_VERSION`, `DEFAULT_MAX_CONCURRENT`, and `DEFAULT_OUTPUT_DIR` from `knmi_dataset_downloader`.

## Download statistics

Each run reports:

- Total files matching the query
- Skipped (already on disk)
- Downloaded
- Failures (with names in `stats.failed_files`)
- Total bytes downloaded

## Configuration

There is **no** `DATASET_OUTPUT_DIR` environment variable in this package. Outputs go to:

- **Default:** `./datasets` (see `DEFAULT_OUTPUT_DIR` in `knmi_dataset_downloader.defaults`), or
- **CLI:** `--output-dir` / `-o`, or
- **API:** `output_dir=` on `download()`.

## Error handling

- Existing files are skipped (not re-downloaded by default).
- Partial files are removed if a download fails.
- Failures are logged and listed on `DownloadStats.failed_files`.

Heavy use of the **anonymous** Open Data API can result in **HTTP 429**; KNMI may require a **cooldown** (on the order of an hour) before retrying.

## Developing

- **Tests:** `pytest` with `pytest-asyncio` (`uv run pytest` or `pytest tests` with dev deps installed).
- **Lint / types:** `uv run ruff check src tests`, `uv run basedpyright src tests` (see `pyproject.toml`).
- **Integration tests** call the real KNMI API; they may **skip** on 429.

## Contributing

Contributions are welcome. Please open a Pull Request; for larger changes, open an issue first.

## License

This project is licensed under the GNU General Public License v3.0 or later — see the [LICENSE](LICENSE) file.

## Acknowledgments

- KNMI for the Data Platform API
- Async I/O via `asyncio` and `httpx`

## Support

Problems or suggestions: [open an issue](https://github.com/tiborrr/knmi-dataset-downloader/issues).
