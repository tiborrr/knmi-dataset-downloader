import unittest
from src.knmi_dataset_downloader.api_key import get_anonymous_api_key

class TestApiKey(unittest.IsolatedAsyncioTestCase):
    """Test cases for the api_key module."""

    async def test_anonymous_api_key_fetch(self):
        """Test fetching the anonymous API key from KNMI developer portal.
        This test makes a real HTTP request to the portal."""
        api_key = await get_anonymous_api_key()
        
        # Verify we got a valid API key
        self.assertIsInstance(api_key, str)
        self.assertTrue(len(api_key) > 0)
        # The key should start with 'eyJ' (base64 encoded JSON)
        self.assertTrue(api_key.startswith('eyJ'))
        # Should be a base64 string (only contains valid base64 characters)
        self.assertTrue(all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-' for c in api_key))

if __name__ == '__main__':
    unittest.main() 