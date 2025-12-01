"""
Test pour vérifier que les clés API sont correctement décryptées et disponibles.
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.data_manager import DataManager

def test_api_key_decryption():
    """Test du décryptage des clés API."""
    dm = DataManager()
    
    # Récupérer les settings (avec décryptage automatique)
    settings = dm.get_settings()
    
    print("=== Configuration actuelle ===")
    print(f"Provider actuel: {settings.get('current_provider')}")
    print(f"\n=== Clés API disponibles (décryptées) ===")
    
    api_keys = settings.get('api_keys', {})
    for provider, key in api_keys.items():
        # Afficher les 10 premiers et 10 derniers caractères
        if key:
            masked_key = f"{key[:10]}...{key[-10:]}" if len(key) > 20 else key
            print(f"  ✅ {provider}: {masked_key}")
        else:
            print(f"  ❌ {provider}: [VIDE]")
    
    print(f"\n=== Test pour ScrapeGraphAI ===")
    # L'AIScraper utilise toujours OpenAI par défaut (ligne 347 de chat_page.py)
    # Donc il a besoin de la clé "OpenAI GPT-4o mini"
    openai_key = api_keys.get("OpenAI GPT-4o mini")
    if openai_key:
        print(f"✅ Clé OpenAI trouvée pour ScrapeGraphAI: {openai_key[:15]}...")
        print(f"   Longueur: {len(openai_key)} caractères")
        # Vérifier si elle commence par "sk-" (format OpenAI)
        if openai_key.startswith("sk-"):
            print("   ✅ Format OpenAI valide (commence par 'sk-')")
        else:
            print(f"   ⚠️  Format inattendu (devrait commencer par 'sk-', commence par '{openai_key[:3]}')")
    else:
        print("❌ Aucune clé OpenAI configurée !")
        print("   ScrapeGraphAI ne pourra pas fonctionner.")

if __name__ == "__main__":
    test_api_key_decryption()
