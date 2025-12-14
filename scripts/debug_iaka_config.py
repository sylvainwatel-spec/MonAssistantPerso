
import sys
import os

# Add root to sys.path
sys.path.append(os.getcwd())

from utils.data_manager import DataManager

def debug_iaka():
    dm = DataManager()
    settings = dm.get_settings()
    
    provider = "IAKA (Interne)"
    
    print(f"--- Debugging Provider: {provider} ---")
    
    # Check Key
    keys = settings.get("api_keys", {})
    key = keys.get(provider)
    if key:
        print(f"[OK] Key found: {key[:5]}... (length: {len(key)})")
    else:
        print("[FAIL] No API Key found for this exact provider name.")
        print(f"Available keys for: {list(keys.keys())}")

    # Check Endpoint
    endpoints = settings.get("endpoints", {})
    endpoint = endpoints.get(provider)
    if endpoint:
        print(f"[OK] Endpoint found: {endpoint}")
    else:
        print("[FAIL] No Endpoint found for this exact provider name.")
        print(f"Available endpoints for: {list(endpoints.keys())}")

    # Check Model
    models = settings.get("models", {})
    model = models.get(provider)
    print(f"Model configured: {model} (Default will be 'mistral-small' if None)")

if __name__ == "__main__":
    debug_iaka()
