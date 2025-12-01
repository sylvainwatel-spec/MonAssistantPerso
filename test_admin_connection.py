# NOTE: Ce fichier a été déplacé vers le répertoire tests/. Le code original se trouve désormais dans tests/test_admin_connection.py

import io
import traceback
from utils.data_manager import DataManager
from utils.llm_connector import LLMConnectionTester

# Force UTF-8 for stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_admin_connections():
    print("=== Test Reproduction Admin Connection ===\n")
    
    dm = DataManager()
    settings = dm.get_settings()
    api_keys = settings.get("api_keys", {})
    
    print(f"Clés disponibles pour : {list(api_keys.keys())}")
    
    for provider, key in api_keys.items():
        print(f"\n--- Test de {provider} ---")
        print(f"Clé (premiers cars): {key[:5]}...")
        
        # Simulation de ce que fait AdminFrame.test_connection
        try:
            # Note: IAKA needs an endpoint, others don't
            endpoint = settings.get("endpoints", {}).get(provider) if "IAKA" in provider else None
            
            success, message = LLMConnectionTester.test_provider(provider, key, base_url=endpoint)
            
            if success:
                print(f"✅ SUCCÈS")
                print(f"Message: {message.splitlines()[0]}")
            else:
                print(f"❌ ÉCHEC")
                print(f"Message: {message}")
                
        except Exception as e:
            print(f"❌ ERREUR CRITIQUE lors de l'appel: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    test_admin_connections()
