
import sys
import os

# Add the project root to sys.path
sys.path.append(os.getcwd())

from core.services.llm_service import LLMService

def test_deepseek_connection_logic():
    print("Testing DeepSeek connection logic with empty base_url...")
    
    # Mock data
    provider = "DeepSeek"
    api_key = "sk-fake-key"
    messages = [{"role": "user", "content": "Hello"}]
    # Simulate UI passing empty string for base_url
    kwargs = {"base_url": ""}
    
    # We expect this to try connecting to https://api.deepseek.com
    # and fail with an API error (401), NOT a connection error (unless network is down).
    # But definitely NOT "URL de base (Endpoint) manquante" or generic connection failure due to empty URL.
    
    success, msg = LLMService.generate_response(provider, api_key, messages, **kwargs)
    
    print(f"Success: {success}")
    print(f"Message: {msg}")

    if "401" in msg or "Authentication" in msg or "Unauthorized" in msg:
         print("TEST PASSED: Connection attempted to valid URL (received 401 as expected with fake key).")
    elif "Connection error" in msg:
         print("TEST FAILED: Still getting Connection error. Check if URL is correct.")
    else:
         print(f"TEST RESULT UNCERTAIN: Received: {msg}")

if __name__ == "__main__":
    test_deepseek_connection_logic()
