import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.web_scraper import WebScraper

def test_leboncoin():
    scraper = WebScraper()
    url = "https://www.leboncoin.fr/"
    print(f"Testing access to {url}...")
    
    soup = scraper.fetch_page(url)
    
    if soup:
        print("Successfully fetched page.")
        title = soup.title.string if soup.title else "No title"
        print(f"Page Title: {title}")
        
        # Try to find some content to verify it's not a captcha page
        text = scraper.extract_text(soup)
        print(f"Extracted text length: {len(text)}")
        print("First 500 chars:")
        print(text[:500])
        
        if "datadome" in text.lower() or "captcha" in text.lower():
            print("\nWARNING: Likely blocked by anti-bot protection (Datadome/Captcha detected).")
    else:
        print("Failed to fetch page.")

def test_search():
    scraper = WebScraper()
    url = "https://www.leboncoin.fr/"
    query = "iphone"
    print(f"Testing search on {url} with query '{query}'...")
    
    result = scraper.perform_search(url, query)
    print("Search Result Preview:")
    print(result[:500] if result else "No result")

if __name__ == "__main__":
    test_leboncoin()
    test_search()
