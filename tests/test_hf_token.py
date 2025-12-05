"""Script de test pour vérifier le token Hugging Face"""
import json
import sys
sys.path.insert(0, '.')

from utils.data_manager import DataManager

# Créer une instance du DataManager
dm = DataManager()

# Récupérer les settings (avec décryptage automatique)
settings = dm.get_settings()

# Récupérer le token Hugging Face
hf_token = settings.get('api_keys', {}).get('Hugging Face (Mistral/Mixtral)')

print("=" * 60)
print("VÉRIFICATION DU TOKEN HUGGING FACE")
print("=" * 60)

if hf_token:
    print(f"\n✅ Token trouvé !")
    print(f"Longueur : {len(hf_token)} caractères")
    print(f"Commence par 'hf_' : {hf_token.startswith('hf_')}")
    print(f"Contient des espaces : {' ' in hf_token}")
    print(f"Contient des retours à la ligne : {'\\n' in hf_token or '\\r' in hf_token}")
    print(f"\nPremiers caractères : {hf_token[:10]}...")
    print(f"Derniers caractères : ...{hf_token[-10:]}")
    
    # Test de l'API
    print("\n" + "-" * 60)
    print("TEST DE L'API HUGGING FACE")
    print("-" * 60)
    
    try:
        from huggingface_hub import InferenceClient
        
        # Nettoyer le token (enlever espaces et retours à la ligne)
        clean_token = hf_token.strip()
        
        print(f"\nToken nettoyé :")
        print(f"  Longueur : {len(clean_token)} caractères")
        print(f"  Identique à l'original : {clean_token == hf_token}")
        
        client = InferenceClient(token=clean_token)
        
        response = client.chat_completion(
            messages=[{"role": "user", "content": "Hello"}],
            model="Qwen/Qwen2.5-72B-Instruct",
            max_tokens=10
        )
        
        content = response.choices[0].message.content
        print(f"\n✅ TEST RÉUSSI !")
        print(f"Réponse : {content}")
        
    except Exception as e:
        print(f"\n❌ TEST ÉCHOUÉ !")
        print(f"Erreur : {str(e)}")
        
else:
    print("\n❌ Token non trouvé !")
    print("Clés disponibles :", list(settings.get('api_keys', {}).keys()))

print("\n" + "=" * 60)
