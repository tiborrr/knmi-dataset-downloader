import unittest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime
import argparse
from pathlib import Path
from src.knmi_dataset_downloader.cli import async_main, parse_date
from src.knmi_dataset_downloader import Downloader
from src.knmi_dataset_downloader.api_key import get_anonymous_api_key
from src.knmi_dataset_downloader.defaults import (
    DEFAULT_OUTPUT_DIR,
    DEFAULT_DATASET_NAME,
    DEFAULT_DATASET_VERSION,
    DEFAULT_MAX_CONCURRENT,
)

class TestCLI(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        """Set up test fixtures."""
        # Anonymous key from https://developer.dataplatform.knmi.nl/open-data-api#token
        self.api_key = asyncio.run(get_anonymous_api_key())
        # Create test downloads directory
        self.test_output_dir = Path('test_downloads')
        self.test_output_dir.mkdir(exist_ok=True)

    def tearDown(self):
        """Clean up test files."""
        # Remove all .nc files in test directory
        for nc_file in self.test_output_dir.glob('*.nc'):
            nc_file.unlink()
        # Try to remove directory (will only work if empty)
        try:
            self.test_output_dir.rmdir()
        except OSError:
            pass

    async def test_parse_date(self):
        """Test date parsing functionality."""
        # Test valid dates in different ISO 8601 formats
        self.assertEqual(parse_date("2023-01-01T00:00:00"), datetime(2023, 1, 1, 0, 0, 0))
        self.assertEqual(parse_date("2023-01-01T12:30:45"), datetime(2023, 1, 1, 12, 30, 45))
        self.assertEqual(parse_date("2023-01-01"), datetime(2023, 1, 1))
        
        # Test empty date
        self.assertIsNone(parse_date(""))
        
        # Test invalid date formats
        with self.assertRaises(argparse.ArgumentTypeError):
            parse_date("2023/01/01")
        with self.assertRaises(argparse.ArgumentTypeError):
            parse_date("invalid")
        with self.assertRaises(argparse.ArgumentTypeError):
            parse_date("2023-13-01")  # Invalid month

    async def test_cli_with_real_api(self):
        """Test CLI with real API using anonymous key."""
        test_args = [
            '--api-key', self.api_key,
            '--dataset', DEFAULT_DATASET_NAME,
            '--version', DEFAULT_DATASET_VERSION,
            '--start-date', '2024-01-01T00:00:00',
            '--end-date', '2024-01-01T00:20:00',    # Just 20 minutes of data
            '--concurrent', '2',
            '--output-dir', str(self.test_output_dir)  # Test with custom output directory
        ]
        with patch('sys.argv', ['knmi-download'] + test_args):
            await async_main()  # This will actually download data
            
            # Verify that at least one .nc file was downloaded
            nc_files = list(self.test_output_dir.glob('*.nc'))
            self.assertGreater(len(nc_files), 0, 
                             "No .nc files were downloaded. The default dataset should contain .nc files.")

    async def test_cli_with_defaults(self):
        """Test CLI with default arguments (no dates specified)."""
        test_args = [
            '--output-dir', str(self.test_output_dir)  # Only specify output dir for testing
        ]
        
        with patch('sys.argv', ['knmi-download'] + test_args):
            await async_main()
            
            # Verify files were downloaded
            nc_files = list(self.test_output_dir.glob('*.nc'))
            self.assertGreater(len(nc_files), 0, 
                             "No .nc files were downloaded with default arguments")

if __name__ == '__main__':
    unittest.main() 