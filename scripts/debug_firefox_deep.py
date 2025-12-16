from playwright.sync_api import sync_playwright
import os
import shutil
import tempfile

def test_firefox_deep():
    print("🕵️ Deep Testing Firefox Launch...")
    
    # Locate Firefox
    paths = [
        r"C:\Program Files\Mozilla Firefox\firefox.exe",
        os.path.join(os.getenv('ProgramFiles', ''), 'Mozilla Firefox', 'firefox.exe'),
        os.path.join(os.getenv('ProgramFiles(x86)', ''), 'Mozilla Firefox', 'firefox.exe'),
    ]
    executable_path = next((p for p in paths if p and os.path.exists(p)), None)
    
    if not executable_path:
        print("❌ Firefox executable not found.")
        return
    print(f"👉 Executable: {executable_path}")

    configs = [
        {
            "name": "Headless=True", 
            "kwargs": {"headless": True}
        },
        {
            "name": "Headless=False (Visible)", 
            "kwargs": {"headless": False}
        },
        {
            "name": "Visible + No Remote", 
            "kwargs": {"headless": False, "args": ["-no-remote"]}
        },
        {
            "name": "Visible + New Instance", 
            "kwargs": {"headless": False, "args": ["-new-instance"]}
        }
    ]

    with sync_playwright() as p:
        for config in configs:
            print(f"\n🧪 Testing Config: {config['name']}...")
            try:
                browser = p.firefox.launch(
                    executable_path=executable_path,
                    **config['kwargs']
                )
                print(f"   ✅ LAUNCH SUCCESS! ({config['name']})")
                page = browser.new_page()
                print("   📄 Page created.")
                page.close()
                browser.close()
                print("   🔒 Closed.")
                return # Stop after first success
            except Exception as e:
                print(f"   ❌ FAILED: {e}")

if __name__ == "__main__":
    test_firefox_deep()
