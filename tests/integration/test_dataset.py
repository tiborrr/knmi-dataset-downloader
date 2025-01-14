import unittest
import os
from datetime import datetime
import tempfile
from pathlib import Path
import shutil

from src.knmi_dataset_downloader import download, DownloadStats
from src.knmi_dataset_downloader.api_key import get_anonymous_api_key

class TestDownloader(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        """Set up test fixtures."""
        # self.api_key = await get_anonymous_api_key()
        self.api_key = "eyJvcmciOiI1ZTU1NGUxOTI3NGE5NjAwMDEyYTNlYjEiLCJpZCI6IjI0N2M3NDRkNjdhOTQ0NGY5ODdjYmFlNjllYjhmZGY5IiwiaCI6Im11cm11cjEyOCJ9"
        # Create a temporary directory for test outputs
        self.temp_dir = Path(tempfile.mkdtemp())

    def test_download_stats(self):
        """Test DownloadStats initialization and updates."""
        stats = DownloadStats()
        self.assertEqual(stats.total_files, 0)
        self.assertEqual(stats.skipped_files, 0)
        self.assertEqual(stats.downloaded_files, 0)
        self.assertEqual(stats.failed_files, [])
        self.assertEqual(stats.total_bytes_downloaded, 0)

    async def test_download(self):
        """Test file download functionality."""
        # Test with a small date range and limit to 1 file
        start_date = datetime(2024, 1, 1, 0, 0, 0)
        end_date = datetime(2024, 1, 1, 0, 30, 0)  # Just 30 minutes
        
        try:
            stats = await download(
                api_key=self.api_key,
                output_dir=self.temp_dir,
                start_date=start_date,
                end_date=end_date,
                limit=1
            )
            # Check if stats were updated
            self.assertEqual(stats.total_files, 1, "Should only download 1 file")
            self.assertLessEqual(stats.downloaded_files + stats.skipped_files, 1)
            self.assertEqual(len(stats.failed_files), 0, "No files should fail")
        except Exception as e:
            self.fail(f"Download failed with error: {str(e)}")

    async def test_download_with_limit(self):
        """Test download limit functionality."""
        start_date = datetime(2024, 1, 1, 0, 0, 0)
        end_date = datetime(2024, 1, 1, 23, 59, 59)  # Full day
        
        # Test with different limits
        for limit in [1, 2]:
            # Create a separate temp dir for each test to avoid conflicts
            stats = await download(
                api_key=self.api_key,
                output_dir=self.temp_dir,
                start_date=start_date,
                end_date=end_date,
                limit=limit
            )
            self.assertEqual(stats.total_files, limit, 
                            f"Should limit to {limit} files")
            self.assertLessEqual(
                stats.downloaded_files + stats.skipped_files,
                limit,
                f"Total processed files should not exceed limit of {limit}"
            )

    async def asyncTearDown(self):
        """Clean up after tests."""
        # Clean up the temp directory
        if hasattr(self, 'temp_dir'):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

if __name__ == '__main__':
    unittest.main() 