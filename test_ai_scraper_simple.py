"""
Test simple pour vérifier que AIScraper fonctionne sans l'erreur 'thinking'.
"""
import utils.patch_langchain
from utils.ai_scraper import AIScraper

def test_ai_scraper_init():
    """Test de l'initialisation du scraper IA."""
    try:
        # Créer le scraper avec une clé factice
        scraper = AIScraper(
            api_key="sk-test-key",
            model="gpt-4o-mini",
            provider="openai"
        )
        print("✅ AIScraper initialisé avec succès")
        print(f"   Modèle: {scraper.model}")
        print(f"   Provider: {scraper.provider}")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_ai_scraper_init()
    if success:
        print("\n🎉 Test réussi ! Le problème 'thinking' semble résolu.")
    else:
        print("\n⚠️  Le problème persiste.")
