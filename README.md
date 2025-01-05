# KNMI Dataset Downloader

A Python package for easily downloading datasets from the KNMI (Royal Netherlands Meteorological Institute) Data Platform. This tool supports concurrent downloads and provides both a command-line interface and a Python API.

## Features

- Concurrent downloads for improved performance
- Progress bars for both overall and individual file downloads
- Support for date range filtering
- Skips already downloaded files
- Both CLI and Python API interfaces
- Detailed download statistics
- Anonymous API key support with automatic fetching
- Built with Kiota-generated API client for type-safe KNMI API interactions
- Request timeouts for improved reliability

## Installation

You can install the package using pip:

```bash
pip install knmi-dataset-downloader
```

## Prerequisites

- Python 3.7 or higher
- A KNMI Data Platform API key (optional - will use anonymous API key if not provided)

## Usage

### Command Line Interface

The simplest way to use the downloader is through the command line:

```bash
# Using your own API key
knmi-download --api-key YOUR_API_KEY --start-date 2024-01-01 --end-date 2024-01-31

# Using anonymous API key (automatically fetched)
knmi-download --start-date 2024-01-01 --end-date 2024-01-31
```

Available options:

```bash
Options:
  -d, --dataset TEXT     Name of the dataset to download (default: Actuele10mindataKNMIstations)
  -v, --version TEXT     Version of the dataset (default: 2)
  -c, --concurrent INT   Maximum number of concurrent downloads (default: 10)
  -s, --start-date TEXT  Start date in ISO 8601 format (YYYY-MM-DD or YYYY-MM-DDThh:mm:ss)
  -e, --end-date TEXT    End date in ISO 8601 format (YYYY-MM-DD or YYYY-MM-DDThh:mm:ss)
  --api-key TEXT         KNMI API key [optional - will use anonymous API key if not provided]
  -o, --output-dir PATH  Output directory for downloaded files
  --help                 Show this message and exit
```

### Python API

You can also use the package in your Python code:

```python
from knmi_dataset_downloader import KNMIDataset
import asyncio
from datetime import datetime

async def main():
    # Initialize the downloader with your own API key
    downloader = KNMIDataset(
        dataset_name="Actuele10mindataKNMIstations",
        version="2",
        max_concurrent=10,
        api_key="YOUR_API_KEY"  # Optional - will use anonymous API key if not provided
    )
    
    # Download files for a specific date range
    await downloader.download(
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 1, 31)
    )

# Run the download
if __name__ == "__main__":
    asyncio.run(main())
```

## Download Statistics

After each download session, the tool provides detailed statistics including:
- Total number of files found
- Number of files already present (skipped)
- Number of files downloaded
- Number of failed downloads
- Total data downloaded
- List of any failed downloads

## Configuration

By default, files are downloaded to a directory specified by `DATASET_OUTPUT_DIR` in your configuration. You can modify this by setting the appropriate environment variable or updating the config file.

## Error Handling

- The downloader automatically skips existing files
- Partially downloaded files are removed in case of failures
- Failed downloads are logged and reported in the final statistics

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the GNU General Public License v3.0 - see the LICENSE file for details.

## Acknowledgments

- KNMI for providing the Data Platform API
- Built with Python's asyncio for efficient concurrent downloads

## Support

If you encounter any problems or have suggestions, please [open an issue](https://github.com/tiborrr/knmi-dataset-downloader/issues) on GitHub.
