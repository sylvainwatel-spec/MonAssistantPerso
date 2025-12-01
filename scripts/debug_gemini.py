
import json
import os
import sys

# Ajouter le répertoire parent au path pour importer les modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    import google.generativeai as genai
    print(f"Google Generative AI version: {genai.__version__}")
except ImportError:
    print("Google Generative AI not installed.")
    sys.exit(1)

def load_api_key():
    try:
        # Load encryption key
        key_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.secret.key')
        if os.path.exists(key_path):
            with open(key_path, 'rb') as kf:
                fernet_key = kf.read()
                from cryptography.fernet import Fernet
                cipher = Fernet(fernet_key)
        else:
            print("No .secret.key found")
            return None

        with open('settings.json', 'r', encoding='utf-8') as f:
            settings = json.load(f)
            api_keys = settings.get('api_keys', {})
            encrypted_key = api_keys.get('Google Gemini 1.5 Flash') or api_keys.get('Google Gemini')
            
            if encrypted_key:
                try:
                    return cipher.decrypt(encrypted_key.encode()).decode()
                except Exception as e:
                    print(f"Decryption failed: {e}")
                    return encrypted_key # Return raw if decryption fails (maybe it wasn't encrypted?)
            return None
    except Exception as e:
        print(f"Error loading settings: {e}")
        return None

def test_connection():
    api_key = load_api_key()
    if not api_key:
        print("No API key found for Google Gemini in settings.json")
        return

    print(f"Testing with API Key: {api_key[:5]}...")
    genai.configure(api_key=api_key)

    print("\nListing available models...")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
    except Exception as e:
        print(f"Error listing models: {e}")

    models_to_test = [
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-pro"
    ]

    for model_name in models_to_test:
        print(f"\nTesting model: {model_name}")
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Hello")
            print(f"SUCCESS! Response: {response.text[:50]}...")
            return
        except Exception as e:
            print(f"FAILED: {e}")

    print("\nAll models failed.")

if __name__ == "__main__":
    test_connection()
