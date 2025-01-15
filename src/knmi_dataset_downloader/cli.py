from __future__ import annotations

import argparse
import asyncio
from datetime import datetime
from pathlib import Path
from . import dataset
from .defaults import (
    DEFAULT_OUTPUT_DIR,
    DEFAULT_DATASET_NAME,
    DEFAULT_DATASET_VERSION,
    DEFAULT_MAX_CONCURRENT,
    DEFAULT_TIME_WINDOW,
    get_default_date_range,
)
from .api_key import get_anonymous_api_key

def parse_date(date_str: str) -> datetime | None:
    """Parse date string in ISO 8601 format (e.g., 2024-01-01T00:00:00 or 2024-01-01)."""
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        raise argparse.ArgumentTypeError(
            "Date must be in ISO 8601 format (e.g., 2024-01-01T00:00:00 or 2024-01-01)"
        )

async def async_main() -> None:
    """Download KNMI dataset files."""
    parser = argparse.ArgumentParser(
        description="Download KNMI dataset files.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Get default dates
    default_start, default_end = get_default_date_range()
    
    parser.add_argument(
        '-d', '--dataset',
        default=DEFAULT_DATASET_NAME,
        help=f'Name of the dataset to download (default: {DEFAULT_DATASET_NAME})'
    )
    parser.add_argument(
        '-v', '--version',
        default=DEFAULT_DATASET_VERSION,
        help=f'Version of the dataset (default: {DEFAULT_DATASET_VERSION})'
    )
    parser.add_argument(
        '-c', '--concurrent',
        type=int,
        default=DEFAULT_MAX_CONCURRENT,
        help=f'Maximum number of concurrent downloads (default: {DEFAULT_MAX_CONCURRENT})'
    )
    parser.add_argument(
        '-s', '--start-date',
        default=default_start.isoformat(),
        help=f'Start date in ISO 8601 format (e.g., 2024-01-01T00:00:00 or 2024-01-01)\n'
             f'Default is {DEFAULT_TIME_WINDOW.total_seconds() / 60} minutes ago'
    )
    parser.add_argument(
        '-e', '--end-date',
        default=default_end.isoformat(),
        help=f'End date in ISO 8601 format (e.g., 2024-01-01T00:00:00 or 2024-01-01)\n'
             f'Default is now'
    )
    parser.add_argument(
        '--api-key',
        help='KNMI API key (optional - will fetch anonymous API key if not provided)'
    )
    parser.add_argument(
        '-o', '--output-dir',
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help='Output directory for downloaded files'
    )
    parser.add_argument(
        '--limit',
        type=int,
        help='Maximum number of files to download (optional)'
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
    
    # Download files
    await dataset.download(
        api_key=api_key,
        dataset_name=args.dataset,
        version=args.version,
        max_concurrent=args.concurrent,
        output_dir=args.output_dir,
        start_date=start,
        end_date=end,
        limit=args.limit
    )

def main() -> None:
    """Synchronous wrapper for async_main."""
    asyncio.run(async_main())

if __name__ == '__main__':
    main() 