import unittest
from unittest.mock import MagicMock, patch
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.playwright_scraper import PlaywrightScraper

class TestPlaywrightScraper(unittest.TestCase):
    def setUp(self):
        # Mock ResultsManager to avoid file system operations during init
        with patch('utils.playwright_scraper.ResultsManager') as MockRM:
            self.scraper = PlaywrightScraper(assistant_id="test_id", assistant_name="Test Assistant")
            self.mock_rm = MockRM.return_value

    def test_init(self):
        self.assertEqual(self.scraper.assistant_id, "test_id")
        self.assertEqual(self.scraper.assistant_name, "Test Assistant")

    @patch('playwright.sync_api.sync_playwright')
    def test_enter_exit(self, mock_playwright):
        # Mocking the context manager
        mock_p = MagicMock()
        mock_playwright.return_value.start.return_value = mock_p
        
        # Mock browser launch
        mock_browser = MagicMock()
        mock_p.chromium.launch.return_value = mock_browser
        
        # Mock context
        mock_context = MagicMock()
        mock_browser.new_context.return_value = mock_context
        
        with self.scraper:
            self.assertIsNotNone(self.scraper.playwright)
            self.assertIsNotNone(self.scraper.browser)
            self.assertIsNotNone(self.scraper.context)
        
        # Check if resources were closed
        mock_context.close.assert_called_once()
        mock_browser.close.assert_called_once()
        mock_p.stop.assert_called_once() # or mock_playwright().start().stop()

    @patch('playwright.sync_api.sync_playwright')
    def test_search_generic(self, mock_playwright):
         # Mock setup
        mock_p = MagicMock()
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()
        
        mock_playwright.return_value.start.return_value = mock_p
        mock_p.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        
        # Mock generic scraping logic finding elements
        mock_item = MagicMock()
        # query_selector_all returns a list of items
        mock_page.query_selector_all.return_value = [mock_item]
        
        # Mock extraction from item
        mock_title_elem = MagicMock()
        mock_title_elem.text_content.return_value = "Test Page Title"
        
        # When code calls item.query_selector('h1'), return title elem
        # The code iterates selectors: h1, h2, etc.
        # We make it return something for the first one 'h1'
        mock_item.query_selector.return_value = mock_title_elem
        
        # Mock helper methods to avoid actual saving
        self.scraper._save_results = MagicMock(return_value="path/to/results.json")
        
        # Execute search inside context
        with self.scraper:
            results, filepath = self.scraper.search("https://example.com", "test query")
        
        # Verify
        self.assertIn("Test Page Title", results)
        mock_page.goto.assert_called_with("https://example.com?q=test query", wait_until="networkidle", timeout=30000)

if __name__ == '__main__':
    unittest.main()
