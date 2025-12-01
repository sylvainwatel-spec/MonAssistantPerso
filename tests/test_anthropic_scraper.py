"""
Test spécifique pour ScrapeGraphAI avec Anthropic.
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.ai_scraper import AIScraper
import traceback

def test_anthropic_init():
    print("=== Test ScrapeGraphAI avec Anthropic ===\n")
    
    # Clé dummy pour tester l'init
    api_key = "sk-ant-dummy-key-for-testing"

    try:
        print(f"Tentative d'initialisation avec provider='anthropic' et model='claude-3-haiku-20240307'...")
        
        # Note: AIScraper n'a pas de mapping spécifique pour "anthropic" dans le code actuel
        # Il faut voir comment il gère ça.
        # Si on passe "anthropic" comme provider, mon code fait:
        # if "google"... elif "groq"... elif "openai"... else: rien (donc default)
        
        # Si ScrapeGraphAI reçoit un modèle sans préfixe, il utilise OpenAI par défaut ?
        # Ou alors il faut passer "anthropic/claude-3..." ?
        
        # Testons avec le comportement par défaut de ma classe AIScraper
        scraper = AIScraper(
            api_key=api_key,
            model="claude-3-haiku-20240307",
            provider="anthropic"
        )
        
        print("Lancement d'un scrape simple...")
        scraper.simple_scrape("https://example.com", "test")
        print("✅ Scrape lancé sans erreur d'initialisation")
        
    except Exception as e:
        print(f"\n❌ ERREUR D'INITIALISATION DÉTECTÉE :")
        print(str(e))
        traceback.print_exc()

if __name__ == "__main__":
    test_anthropic_init()
