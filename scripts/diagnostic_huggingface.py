"""Script de diagnostic pour le problème de clé API Hugging Face"""
import json

# Charger les settings
with open('settings.json', 'r', encoding='utf-8') as f:
    settings = json.load(f)

# Charger les assistants
with open('assistants.json', 'r', encoding='utf-8') as f:
    assistants = json.load(f)

print("=" * 60)
print("DIAGNOSTIC - CLÉ API HUGGING FACE")
print("=" * 60)

print("\n1. CLÉS API DISPONIBLES DANS SETTINGS.JSON:")
print("-" * 60)
api_keys = settings.get('api_keys', {})
for provider_name in api_keys.keys():
    print(f"  - '{provider_name}'")

print("\n2. ASSISTANTS CONFIGURÉS:")
print("-" * 60)
for assistant in assistants:
    print(f"\nNom: {assistant.get('name', 'N/A')}")
    print(f"  Provider: '{assistant.get('provider', 'N/A')}'")
    print(f"  ID: {assistant.get('id', 'N/A')}")

print("\n3. VÉRIFICATION DE CORRESPONDANCE:")
print("-" * 60)
for assistant in assistants:
    provider = assistant.get('provider', '')
    has_key = provider in api_keys
    print(f"\nAssistant: {assistant.get('name', 'N/A')}")
    print(f"  Provider: '{provider}'")
    print(f"  Clé trouvée: {'✅ OUI' if has_key else '❌ NON'}")
    if not has_key:
        print(f"  Suggestion: Renommer la clé API ou recréer l'assistant")

print("\n" + "=" * 60)
