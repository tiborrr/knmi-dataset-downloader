import unittest
import asyncio
from datetime import datetime

from src.knmi_dataset_downloader import Downloader
from src.knmi_dataset_downloader.downloader import DownloadStats
from src.knmi_dataset_downloader.api_key import get_anonymous_api_key

class TestDownloader(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.api_key = asyncio.run(get_anonymous_api_key())
        self.dataset = Downloader(
            dataset_name="Actuele10mindataKNMIstations",
            version="2",
            max_concurrent=10,
            api_key=self.api_key
        )

    def test_init(self):
        """Test initialization of Downloader."""
        self.assertEqual(self.dataset.dataset_name, "Actuele10mindataKNMIstations")
        self.assertEqual(self.dataset.version, "2")
        self.assertEqual(self.dataset.max_concurrent, 10)
        self.assertEqual(self.dataset.api_key, self.api_key)
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
        # Test with a small date range to limit the number of files
        start_date = datetime(2024, 1, 1, 0, 0, 0)
        end_date = datetime(2024, 1, 1, 0, 30, 0)  # Just 30 minutes
        
        try:
            await self.dataset.download(start_date, end_date)
            # Check if stats were updated
            self.assertGreaterEqual(self.dataset.stats.total_files, 0)
            self.assertGreaterEqual(self.dataset.stats.downloaded_files, 0)
            self.assertGreaterEqual(self.dataset.stats.skipped_files, 0)
        except Exception as e:
            self.fail(f"Download failed with error: {str(e)}")

    def tearDown(self):
        """Clean up after tests."""
        if hasattr(self, 'dataset') and self.dataset.http_client:
            import asyncio
            asyncio.run(self.dataset.http_client.aclose())

if __name__ == '__main__':
    unittest.main() 