
import sys
import os

# Add root to sys.path
sys.path.append(os.getcwd())

from utils.data_manager import DataManager

def check_alternatives():
    dm = DataManager()
    settings = dm.get_settings()
    keys = settings.get("api_keys", {})
    
    providers_to_check = [
        "Meta Llama 3 (via Groq)",
        "Mistral NeMo",
        "Hugging Face (Mistral/Mixtral)",
        "OpenAI GPT-4o mini"
    ]
    
    print("--- Checking Alternative Providers ---")
    for provider in providers_to_check:
        key = keys.get(provider)
        status = "[OK] Key present" if key else "[MISSING] No key found"
        print(f"{provider}: {status}")

if __name__ == "__main__":
    check_alternatives()
