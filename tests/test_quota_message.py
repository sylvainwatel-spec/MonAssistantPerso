"""
Test pour vérifier que le message d'erreur de quota est clair.
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.data_manager import DataManager
from utils.ai_scraper import AIScraper

def test_quota_error_message():
    """Test du message d'erreur de quota."""
    dm = DataManager()
    settings = dm.get_settings()
    
    # Récupérer la clé OpenAI
    api_key = settings.get('api_keys', {}).get('OpenAI GPT-4o mini')
    
    print("=== Test du Message d'Erreur de Quota ===\n")
    
    # Créer l'AIScraper
    ai_scraper = AIScraper(
        api_key=api_key,
        model="gpt-4o-mini",
        provider="openai"
    )
    
    # Tenter un scraping qui va échouer avec l'erreur de quota
    result = ai_scraper.simple_scrape(
        url="https://example.com",
        extraction_prompt="Extraire le titre"
    )
    
    print("Message retourné à l'utilisateur :")
    print("=" * 60)
    print(result)
    print("=" * 60)
    
    # Vérifier que le message contient les informations clés
    if "Quota API dépassé" in result:
        print("\n✅ Le message détecte correctement l'erreur de quota")
    if "platform.openai.com" in result:
        print("✅ Le message contient le lien vers la facturation OpenAI")
    if "Gemini" in result or "Groq" in result:
        print("✅ Le message suggère des alternatives")

if __name__ == "__main__":
    test_quota_error_message()
