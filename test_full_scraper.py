"""
Test complet de ScrapeGraphAI avec la vraie clé API décryptée.
"""
from utils.data_manager import DataManager
from utils.ai_scraper import AIScraper

def test_scrapegraph_with_real_key():
    """Test ScrapeGraphAI avec la clé API réelle."""
    dm = DataManager()
    settings = dm.get_settings()
    
    # Récupérer la clé OpenAI (déjà décryptée)
    api_key = settings.get('api_keys', {}).get('OpenAI GPT-4o mini')
    
    if not api_key:
        print("❌ Aucune clé OpenAI trouvée!")
        return False
    
    print(f"✅ Clé API récupérée: {api_key[:15]}... (longueur: {len(api_key)})")
    
    try:
        # Créer l'AIScraper comme dans chat_page.py
        print("\n📦 Création de l'AIScraper...")
        ai_scraper = AIScraper(
            api_key=api_key,
            model="gpt-4o-mini",
            provider="openai"
        )
        print("✅ AIScraper créé avec succès")
        
        # Test simple avec une URL statique
        print("\n🔍 Test de scraping simple...")
        result = ai_scraper.simple_scrape(
            url="https://example.com",
            extraction_prompt="Extraire le titre principal de la page"
        )
        
        print(f"\n📊 Résultat du scraping:")
        print(result)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_scrapegraph_with_real_key()
    if success:
        print("\n🎉 Test réussi - ScrapeGraphAI fonctionne avec la clé API!")
    else:
        print("\n⚠️  Des problèmes persistent.")
