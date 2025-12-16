from playwright.sync_api import sync_playwright
import os

def test_firefox():
    print("Testing Firefox Launch...")
    
    # Path logic from the scraper
    program_files = os.getenv('ProgramFiles', '')
    program_files_x86 = os.getenv('ProgramFiles(x86)', '')
    
    paths = [
        r"C:\Program Files\Mozilla Firefox\firefox.exe",
        os.path.join(program_files, 'Mozilla Firefox', 'firefox.exe'),
        os.path.join(program_files_x86, 'Mozilla Firefox', 'firefox.exe'),
    ]
    
    executable_path = None
    for path in paths:
        if path and os.path.exists(path):
            executable_path = path
            break
            
    if not executable_path:
        print("❌ Firefox executable not found.")
        return

    print(f"Found Firefox: {executable_path}")

    with sync_playwright() as p:
        try:
            print("Attempting to launch (headless=True)...")
            browser = p.firefox.launch(
                executable_path=executable_path,
                headless=True
            )
            print("✅ Launch successful!")
            page = browser.new_page()
            print("Page created.")
            browser.close()
        except Exception as e:
            print(f"❌ Launch failed: {e}")

if __name__ == "__main__":
    test_firefox()
