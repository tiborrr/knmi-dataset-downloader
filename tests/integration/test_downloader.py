import unittest
from datetime import datetime
import tempfile
from pathlib import Path
import shutil

from src.knmi_dataset_downloader import Downloader
from src.knmi_dataset_downloader.downloader import DownloadStats
from src.knmi_dataset_downloader.api_key import get_anonymous_api_key

class TestDownloader(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        """Set up test fixtures."""
        self.api_key = await get_anonymous_api_key()
        # Create a temporary directory for test outputs
        self.temp_dir = Path(tempfile.mkdtemp())
        self.dataset = Downloader(
            dataset_name="Actuele10mindataKNMIstations",
            version="2",
            max_concurrent=10,
            api_key=self.api_key,
            output_dir=self.temp_dir
        )

    def test_init(self):
        """Test initialization of Downloader."""
        self.assertEqual(self.dataset.dataset_name, "Actuele10mindataKNMIstations")
        self.assertEqual(self.dataset.version, "2")
        self.assertEqual(self.dataset.max_concurrent, 10)
        self.assertEqual(self.dataset.api_key, self.api_key)
        self.assertEqual(self.dataset.output_dir, self.temp_dir)
        self.assertIsNotNone(self.dataset.semaphore)
        self.assertIsNotNone(self.dataset.client)
        self.assertIsNotNone(self.dataset.http_client)
        self.assertIsInstance(self.dataset.stats, DownloadStats)

    def test_format_size(self):
        """Test size formatting."""
        test_cases = [
            (500, "500.0 B"),
            (1024, "1.0 KB"),
            (1024 * 1024, "1.0 MB"),
            (1024 * 1024 * 1024, "1.0 GB"),
            (1024 * 1024 * 1024 * 1024, "1.0 TB"),
        ]
        for size, expected in test_cases:
            self.assertEqual(self.dataset._format_size(size), expected)

    def test_download_stats(self):
        """Test DownloadStats initialization and updates."""
        stats = DownloadStats()
        self.assertEqual(stats.total_files, 0)
        self.assertEqual(stats.skipped_files, 0)
        self.assertEqual(stats.downloaded_files, 0)
        self.assertEqual(stats.failed_files, [])
        self.assertEqual(stats.total_bytes_downloaded, 0)

    async def test_get_files_list(self):
        """Test getting list of files."""
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 31)
        files = await self.dataset._get_files_list(start_date, end_date)
        self.assertIsInstance(files, list)
        # Note: We can't assert exact file count as it depends on the API response

    async def test_download(self):
        """Test file download functionality."""
        # Test with a small date range and limit to 1 file
        start_date = datetime(2024, 1, 1, 0, 0, 0)
        end_date = datetime(2024, 1, 1, 0, 30, 0)  # Just 30 minutes
        
        try:
            await self.dataset.download(start_date, end_date, limit=1)
            # Check if stats were updated
            self.assertEqual(self.dataset.stats.total_files, 1, "Should only download 1 file")
            self.assertLessEqual(self.dataset.stats.downloaded_files + self.dataset.stats.skipped_files, 1)
            self.assertEqual(len(self.dataset.stats.failed_files), 0, "No files should fail")
        except Exception as e:
            self.fail(f"Download failed with error: {str(e)}")

    async def test_download_with_limit(self):
        """Test download limit functionality."""
        start_date = datetime(2024, 1, 1, 0, 0, 0)
        end_date = datetime(2024, 1, 1, 23, 59, 59)  # Full day
        
        # Test with different limits
        for limit in [1, 2]:
            with self.subTest(limit=limit):
                # Create a separate temp dir for each test to avoid conflicts
                temp_dir = Path(tempfile.mkdtemp())
                dataset = Downloader(
                    dataset_name="Actuele10mindataKNMIstations",
                    version="2",
                    max_concurrent=10,
                    api_key=self.api_key,
                    output_dir=temp_dir
                )
                try:
                    await dataset.download(start_date, end_date, limit=limit)
                    self.assertEqual(dataset.stats.total_files, limit, 
                                  f"Should limit to {limit} files")
                    self.assertLessEqual(
                        dataset.stats.downloaded_files + dataset.stats.skipped_files,
                        limit,
                        f"Total processed files should not exceed limit of {limit}"
                    )
                except Exception as e:
                    self.fail(f"Download with limit {limit} failed with error: {str(e)}")
                finally:
                    await dataset.http_client.aclose()
                    # Clean up the temp directory
                    shutil.rmtree(temp_dir, ignore_errors=True)

    async def asyncTearDown(self):
        """Clean up after tests."""
        if hasattr(self, 'dataset') and self.dataset.http_client:
            await self.dataset.http_client.aclose()
        # Clean up the temp directory
        if hasattr(self, 'temp_dir'):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

if __name__ == '__main__':
    unittest.main() 