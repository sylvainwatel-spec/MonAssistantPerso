"""
Test spécifique pour ScrapeGraphAI avec Groq.
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.data_manager import DataManager
from utils.ai_scraper import AIScraper
import traceback

def test_groq_init():
    print("=== Test ScrapeGraphAI avec Groq ===\n")
    
    dm = DataManager()
    settings = dm.get_settings()
    
    # Récupérer ou définir une clé Groq pour le test
    # (On suppose qu'elle a été sauvegardée par le test précédent)
    provider_name = "Meta Llama 3 (via Groq)"
    api_key = settings.get("api_keys", {}).get(provider_name)
    
    if not api_key:
        print("❌ Pas de clé Groq trouvée. Impossible de tester.")
        # On utilise une clé dummy pour tester au moins l'initialisation
        api_key = "gsk_dummy_key_for_testing_initialization_only"
        print("⚠️ Utilisation d'une clé dummy pour tester l'init.")

    try:
        print(f"Tentative d'initialisation avec provider='groq' et model='llama-3.1-8b-instant'...")
        scraper = AIScraper(
            api_key=api_key,
            model="llama-3.1-8b-instant",
            provider="groq"
        )
        
        # On lance un simple scrape (qui échouera probablement avec la dummy key, mais on veut voir SI ça crash à l'init)
        print("Lancement d'un scrape simple...")
        scraper.simple_scrape("https://example.com", "test")
        print("✅ Scrape lancé sans erreur d'initialisation (le résultat peut être une erreur API, c'est normal)")
        
    except Exception as e:
        print(f"\n❌ ERREUR D'INITIALISATION DÉTECTÉE :")
        print(str(e))
        traceback.print_exc()

if __name__ == "__main__":
    test_groq_init()
