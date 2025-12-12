import sys
import os
import logging

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.playwright_scraper import PlaywrightScraper

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("reproduce_browser")

def log_callback(msg):
    print(f"[CALLBACK] {msg}")

def test_chrome_launch():
    print("=== Testing Chrome Launch ===")
    
    # Initialize scraper with Chrome
    scraper = PlaywrightScraper(
        browser_type="chrome",
        headless=False, # Visible mode requested by user
        log_callback=log_callback
    )
    
    try:
        with scraper:
            print("Browser context entered.")
            if scraper.browser:
                print(f"Browser object: {scraper.browser}")
                # Check if it's actually Chrome (hard to check internal object type easily, but launch logs should tell)
                
            if scraper.context:
                print(f"Context object: {scraper.context}")
                
            # Keep open briefly
            import time
            time.sleep(2)
            
    except Exception as e:
        print(f"CRASH: {e}")

if __name__ == "__main__":
    test_chrome_launch()
