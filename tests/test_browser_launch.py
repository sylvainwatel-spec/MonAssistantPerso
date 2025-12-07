from utils.playwright_scraper import PlaywrightScraper
import logging

logging.basicConfig(level=logging.INFO)

def test_launch_chrome():
    print("Testing Chrome Launch...")
    scraper = PlaywrightScraper(browser_type="chrome", headless=False)
    try:
        with scraper:
            print("Launched Chrome Successfully!")
    except Exception as e:
        print(f"Failed to launch Chrome: {e}")

def test_launch_edge():
    print("\nTesting Edge Launch...")
    scraper = PlaywrightScraper(browser_type="msedge", headless=False)
    try:
        with scraper:
            print("Launched Edge Successfully!")
    except Exception as e:
        print(f"Failed to launch Edge: {e}")

def test_launch_firefox():
    print("\nTesting Firefox Launch...")
    scraper = PlaywrightScraper(browser_type="firefox", headless=True)
    try:
        with scraper:
            print("Launched Firefox Successfully!")
    except Exception as e:
        print(f"Failed to launch Firefox: {e}")

if __name__ == "__main__":
    test_launch_chrome()
    # test_launch_edge()
    test_launch_firefox()
