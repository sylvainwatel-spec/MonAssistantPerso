"""
Test de vérification pour la configuration multi-provider de ScrapeGraphAI.
"""
from utils.data_manager import DataManager
from utils.ai_scraper import AIScraper

def test_scrapegraph_configuration():
    """Test la configuration et l'instanciation de l'AIScraper avec différents providers."""
    print("=== Test de Configuration ScrapeGraphAI ===\n")
    
    dm = DataManager()
    
    # 1. Simuler la sauvegarde d'une configuration
    print("1. Test de sauvegarde de configuration...")
    test_provider = "Meta Llama 3 (via Groq)"
    test_key = "gsk_test_key_12345"
    
    # Récupérer les settings actuels
    settings = dm.get_settings()
    api_keys = settings.get("api_keys", {})
    endpoints = settings.get("endpoints", {})
    
    # Sauvegarder la clé et définir comme provider ScrapeGraphAI
    api_keys[test_provider] = test_key
    dm.save_configuration(
        active_provider="OpenAI GPT-4o mini", # Le provider principal reste OpenAI
        api_keys=api_keys,
        endpoints=endpoints,
        scrapegraph_provider=test_provider
    )
    
    # Recharger pour vérifier
    settings = dm.get_settings()
    saved_sg_provider = settings.get("scrapegraph_provider")
    saved_key = settings.get("api_keys", {}).get(test_provider)
    
    if saved_sg_provider == test_provider:
        print(f"✅ Provider ScrapeGraphAI correctement sauvegardé : {saved_sg_provider}")
    else:
        print(f"❌ Erreur sauvegarde provider : attendu {test_provider}, reçu {saved_sg_provider}")
        
    if saved_key == test_key:
        print(f"✅ Clé API correctement sauvegardée et décryptée")
    else:
        print(f"❌ Erreur sauvegarde clé")

    # 2. Test de l'instanciation de AIScraper
    print("\n2. Test d'instanciation AIScraper...")
    
    # Mapper comme dans chat_page.py
    provider_code = "openai"
    model_code = "gpt-4o-mini"
    
    if "Gemini" in saved_sg_provider:
        provider_code = "google"
        model_code = "gemini-1.5-flash"
    elif "Groq" in saved_sg_provider:
        provider_code = "groq"
        model_code = "llama-3.1-8b-instant"
        
    print(f"Mapping pour {saved_sg_provider}:")
    print(f"  - Provider code: {provider_code}")
    print(f"  - Model code: {model_code}")
    
    try:
        scraper = AIScraper(
            api_key=saved_key,
            model=model_code,
            provider=provider_code
        )
        print("✅ AIScraper instancié avec succès")
        print(f"  - Scraper provider: {scraper.provider}")
        print(f"  - Scraper model: {scraper.model}")
        
        # Vérifier la logique interne de configuration (sans lancer le scrape)
        # On accède aux attributs pour voir si la logique est bonne
        if scraper.provider == "groq":
            print("✅ Le scraper a bien détecté le provider Groq")
        else:
            print(f"❌ Erreur détection provider: {scraper.provider}")
            
    except Exception as e:
        print(f"❌ Erreur lors de l'instanciation: {e}")

if __name__ == "__main__":
    test_scrapegraph_configuration()
