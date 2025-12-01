"""
Test de la logique de connexion du Chat (ChatFrame).
Simule les appels aux différents providers comme le fait chat_page.py.
"""
from utils.data_manager import DataManager
import traceback
import sys

def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', 'replace').decode())

def test_chat_providers():
    safe_print("=== Test de Connexion Chat ===\n")
    
    dm = DataManager()
    settings = dm.get_settings()
    api_keys = settings.get("api_keys", {})
    
    safe_print(f"Providers configurés : {list(api_keys.keys())}")
    
    # Test OpenAI
    if "OpenAI GPT-4o mini" in api_keys:
        safe_print("\n--- Test OpenAI ---")
        try:
            from openai import OpenAI
            key = api_keys["OpenAI GPT-4o mini"]
            client = OpenAI(api_key=key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            safe_print(f"✅ OpenAI Success: {response.choices[0].message.content}")
        except Exception as e:
            safe_print(f"❌ OpenAI Error: {e}")
            # traceback.print_exc() # Avoid clutter

    # Test Groq
    if "Meta Llama 3 (via Groq)" in api_keys:
        safe_print("\n--- Test Groq ---")
        try:
            from groq import Groq
            key = api_keys["Meta Llama 3 (via Groq)"]
            client = Groq(api_key=key)
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            safe_print(f"✅ Groq Success: {response.choices[0].message.content}")
        except Exception as e:
            safe_print(f"❌ Groq Error: {e}")
            traceback.print_exc()

    # Test Gemini
    if "Google Gemini 1.5 Flash" in api_keys:
        safe_print("\n--- Test Gemini ---")
        try:
            import google.generativeai as genai
            key = api_keys["Google Gemini 1.5 Flash"]
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content("Hello")
            safe_print(f"✅ Gemini Success: {response.text}")
        except Exception as e:
            safe_print(f"❌ Gemini Error: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    test_chat_providers()
