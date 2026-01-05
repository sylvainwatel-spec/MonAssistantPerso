import os
import sys

try:
    from openai import OpenAI
except ImportError:
    print("OpenAI not installed")
    sys.exit(1)

def test_empty_base_url():
    print("Testing OpenAI client with base_url='' ...")
    try:
        # We don't need a real key if we expect it to fail on URL parsing/connection init
        # But to be sure it's not key error, let's use a dummy that format-wise is ok-ish or just random
        client = OpenAI(api_key="sk-test-dummy", base_url="")
        print(f"Client created with base_url='{client.base_url}'")
        
        # Valid Default is https://api.openai.com/v1/
        # If base_url is "", it might try to connect to https://models or just fail relative path
        
        try:
            client.models.list()
        except Exception as e:
            print(f"Caught expected error: {e}")
            import traceback
            traceback.print_exc()

    except Exception as e:
        print(f"Initialization error: {e}")

def test_none_base_url():
    print("\nTesting OpenAI client with base_url=None ...")
    try:
        client = OpenAI(api_key="sk-test-dummy", base_url=None)
        print(f"Client created with base_url='{client.base_url}'")
        # This would fail on Auth with dummy key, but connection should be fine (DNS lookup of api.openai.com)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_empty_base_url()
    test_none_base_url()
