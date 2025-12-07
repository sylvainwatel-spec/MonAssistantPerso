import unittest
from unittest.mock import MagicMock, patch
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.scraper_factory import ScraperFactory
from utils.playwright_scraper import PlaywrightScraper

class TestScraperFactory(unittest.TestCase):
    def test_create_playwright(self):
        """Test la création d'un scraper Playwright"""
        scraper = ScraperFactory.create_scraper(
            "playwright", 
            assistant_id="123", 
            assistant_name="Test"
        )
        self.assertIsInstance(scraper, PlaywrightScraper)
        self.assertEqual(scraper.assistant_id, "123")
        self.assertEqual(scraper.assistant_name, "Test")
        
    def test_invalid_scraper_type(self):
        """Test qu'une erreur est levée pour un type inconnu"""
        with self.assertRaises(ValueError):
            ScraperFactory.create_scraper("unknown_type")

    def test_get_available_scrapers(self):
        """Test la méthode de vérification de disponibilité"""
        available = ScraperFactory.get_available_scrapers()
        self.assertIsInstance(available, dict)
        self.assertIn("scrapegraphai", available)
        self.assertIn("playwright", available)
        # On suppose que les deps sont installées dans l'env de dev
        self.assertTrue(available["playwright"])

    def test_get_scraper_info(self):
        """Test la récupération des infos sur les scrapers"""
        info = ScraperFactory.get_scraper_info("playwright")
        self.assertEqual(info["name"], "Playwright")
        self.assertEqual(info["cost"], "Gratuit")
        self.assertFalse(info["requires_api_key"])
        
        info_sg = ScraperFactory.get_scraper_info("scrapegraphai")
        self.assertEqual(info_sg["name"], "ScrapeGraphAI")
        self.assertTrue(info_sg["requires_api_key"])

if __name__ == '__main__':
    unittest.main()
