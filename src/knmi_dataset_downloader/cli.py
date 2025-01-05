from __future__ import annotations

import argparse
import asyncio
from datetime import datetime
from pathlib import Path
from .downloader import Downloader
from .defaults import (
    DEFAULT_OUTPUT_DIR,
    DEFAULT_DATASET_NAME,
    DEFAULT_DATASET_VERSION,
    DEFAULT_MAX_CONCURRENT,
    get_default_date_range,
)
from .api_key import get_anonymous_api_key

def parse_date(date_str: str) -> datetime | None:
    """Parse date string in ISO 8601 format."""
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        raise argparse.ArgumentTypeError("Date must be in ISO 8601 format")

async def async_main() -> None:
    """Download KNMI dataset files."""
    parser = argparse.ArgumentParser(
        description="Download KNMI dataset files.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Get default dates
    default_start, default_end = get_default_date_range()
    
    parser.add_argument(
        '--dataset', '-d',
        default=DEFAULT_DATASET_NAME,
        help='Name of the dataset to download'
    )
    parser.add_argument(
        '--version', '-v',
        default=DEFAULT_DATASET_VERSION,
        help='Version of the dataset'
    )
    parser.add_argument(
        '--concurrent', '-c',
        type=int,
        default=DEFAULT_MAX_CONCURRENT,
        help='Maximum number of concurrent downloads'
    )
    parser.add_argument(
        '--start-date', '-s',
        default=default_start.isoformat(),
        help='Start date in ISO 8601 format example: 2024-01-01T00:00:00 or 2024-01-01, '
             'default is 30 minutes ago'
    )
    parser.add_argument(
        '--end-date', '-e',
        default=default_end.isoformat(),
        help='End date in ISO 8601 format example: 2024-01-01T00:00:00 or 2024-01-01, '
             'default is now'
    )
    parser.add_argument(
        '--api-key',
        help='KNMI API key. If not provided, will attempt to fetch the anonymous API key from the KNMI developer portal.'
    )
    parser.add_argument(
        '--output-dir', '-o',
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help='Output directory for downloaded files'
    )

    args = parser.parse_args()

    # Parse dates
    start = parse_date(args.start_date)
    end = parse_date(args.end_date)
    
    # Get API key - either from args or fetch anonymous key
    api_key = args.api_key
    if not api_key:
        print("No API key provided, fetching anonymous API key from KNMI developer portal...")
        try:
            api_key = await get_anonymous_api_key()
        except Exception as e:
            print(f"Error fetching anonymous API key: {e}")
            print("Please provide an API key using the --api-key argument")
            return
    
    # Initialize downloader
    downloader = Downloader(
        dataset_name=args.dataset,
        version=args.version,
        max_concurrent=args.concurrent,
        api_key=api_key,
        output_dir=args.output_dir
    )
    
    # Download files
    await downloader.download(start_date=start, end_date=end)

def main() -> None:
    """Synchronous wrapper for async_main."""
    asyncio.run(async_main())

if __name__ == '__main__':
    main() 