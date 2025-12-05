"""Test direct de l'appel Hugging Face dans le contexte de l'application"""
import sys
sys.path.insert(0, '.')

from utils.data_manager import DataManager
from huggingface_hub import InferenceClient

# Récupérer le token comme le fait l'application
dm = DataManager()
settings = dm.get_settings()
provider = "Hugging Face (Mistral/Mixtral)"
api_key = settings.get('api_keys', {}).get(provider)

print("=" * 60)
print("TEST HUGGING FACE - CONTEXTE APPLICATION")
print("=" * 60)

print(f"\nProvider: {provider}")
print(f"Token trouvé: {api_key is not None}")

if api_key:
    print(f"Token length: {len(api_key)}")
    print(f"Token type: {type(api_key)}")
    print(f"Token starts with 'hf_': {api_key.startswith('hf_')}")
    print(f"Token (first 10 chars): {api_key[:10]}...")
    
    # Nettoyer le token
    clean_token = api_key.strip()
    print(f"\nToken après .strip():")
    print(f"  Length: {len(clean_token)}")
    print(f"  Identique: {clean_token == api_key}")
    
    # Test 1 : Avec le token original
    print("\n" + "-" * 60)
    print("TEST 1 : Avec token original")
    print("-" * 60)
    try:
        client = InferenceClient(token=api_key)
        response = client.chat_completion(
            messages=[{"role": "user", "content": "Hello"}],
            model="Qwen/Qwen2.5-72B-Instruct",
            max_tokens=10
        )
        print(f"✅ SUCCÈS avec token original")
        print(f"Réponse: {response.choices[0].message.content}")
    except Exception as e:
        print(f"❌ ÉCHEC avec token original")
        print(f"Erreur: {str(e)}")
    
    # Test 2 : Avec le token nettoyé
    print("\n" + "-" * 60)
    print("TEST 2 : Avec token nettoyé (.strip())")
    print("-" * 60)
    try:
        client = InferenceClient(token=clean_token)
        response = client.chat_completion(
            messages=[{"role": "user", "content": "Hello"}],
            model="Qwen/Qwen2.5-72B-Instruct",
            max_tokens=10
        )
        print(f"✅ SUCCÈS avec token nettoyé")
        print(f"Réponse: {response.choices[0].message.content}")
    except Exception as e:
        print(f"❌ ÉCHEC avec token nettoyé")
        print(f"Erreur: {str(e)}")
        
else:
    print("\n❌ Token non trouvé !")
    print("Clés disponibles:", list(settings.get('api_keys', {}).keys()))

print("\n" + "=" * 60)
