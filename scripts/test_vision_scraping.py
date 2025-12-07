import sys
import os
import json
import logging

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.playwright_scraper import PlaywrightScraper
from utils.data_manager import DataManager

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def log_callback(msg):
    print(f"[CALLBACK] {msg}")

def main():
    print("🚀 Démarrage du test de Scraping Vision...")
    
    # 1. Charger les settings avec DataManager (décryptage des clés)
    dm = DataManager()
    settings = dm.get_settings()
    
    api_keys = settings.get("api_keys", {})
    # Chercher clé Gemini
    gemini_key = next((v for k, v in api_keys.items() if "Gemini" in k or "Google" in k), None)
    
    if not gemini_key:
        print("⚠️ Aucune clé Gemini trouvée dans les settings décryptés !")
    else:
        print(f"✅ Clé Gemini trouvée (début: {gemini_key[:5]}...)")

    browser_type = settings.get("scraping_browser", "firefox")
    visible_mode = settings.get("visible_mode", False)
    
    print(f"🔧 Config Loadée: Browser={browser_type}, Visible={visible_mode}")

    # 2. Tech Check module
    try:
        import playwright_stealth
        print("✅ playwright-stealth est installé.")
    except ImportError:
        print("❌ playwright-stealth MANQUANT.")

    # 3. Lancer le Scraper
    scraper = PlaywrightScraper(
        assistant_id="test_vision",
        assistant_name="Tester",
        log_callback=log_callback,
        headless=not visible_mode,
        browser_type=browser_type,
        llm_api_key=gemini_key,
        llm_model="gemini-2.0-flash-exp"
    )

    try:
        with scraper as s:
            print("🌍 Navigation vers LeBonCoin...")
            # Query générique
            # On cherche un truc simple.
            results = s.search("https://www.leboncoin.fr", "iphone 12", "Extraction test par défaut")
            
            print(f"\n📊 RÉSULTATS: {len(results[0])} annonces trouvées.")
            if results[0]:
                print("Exemple:", results[0][0])
            else:
                print("❌ Aucun résultat (Ni CSS ni Vision).")
                
    except Exception as e:
        print(f"\n❌ ERREUR FATALE durant le test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
