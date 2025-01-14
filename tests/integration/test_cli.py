import unittest
import tempfile
from pathlib import Path
import shutil
from unittest.mock import patch

from src.knmi_dataset_downloader.cli import async_main
from src.knmi_dataset_downloader.api_key import get_anonymous_api_key

class TestCLI(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        """Set up test fixtures."""
        self.api_key = await get_anonymous_api_key()
        # Create a temporary directory for test outputs
        self.test_output_dir = Path(tempfile.mkdtemp())

    async def test_cli_with_real_api(self):
        """Test CLI with real API using anonymous key."""
        test_args = [
            '--api-key', self.api_key,
            '--start-date', '2024-01-01T00:00:00',
            '--end-date', '2024-01-01T00:20:00',    # Just 20 minutes of data
            '--concurrent', '2',
            '--output-dir', str(self.test_output_dir),  # Test with custom output directory
            '--limit', '1'  # Limit to 1 file for testing
        ]
        with patch('sys.argv', ['knmi-download'] + test_args):
            await async_main()  # This will actually download data
            
            # Verify that exactly one .nc file was downloaded
            nc_files = list(self.test_output_dir.glob('*.nc'))
            self.assertLessEqual(len(nc_files), 1, 
                             "More than one file was downloaded despite limit=1")
            self.assertGreater(len(nc_files), 0, 
                             "No .nc files were downloaded")

    async def test_cli_with_defaults(self):
        """Test CLI with default arguments (no dates specified)."""
        test_args = [
            '--output-dir', str(self.test_output_dir),  # Only specify output dir for testing
            '--limit', '1'  # Limit to 1 file for testing
        ]
        
        with patch('sys.argv', ['knmi-download'] + test_args):
            await async_main()
            
            # Verify exactly one file was downloaded
            nc_files = list(self.test_output_dir.glob('*.nc'))
            self.assertLessEqual(len(nc_files), 1,
                             "More than one file was downloaded despite limit=1")
            self.assertGreater(len(nc_files), 0,
                             "No .nc files were downloaded with default arguments")

    async def asyncTearDown(self):
        """Clean up after tests."""
        # Clean up the temp directory
        shutil.rmtree(self.test_output_dir, ignore_errors=True)

if __name__ == '__main__':
    unittest.main() 