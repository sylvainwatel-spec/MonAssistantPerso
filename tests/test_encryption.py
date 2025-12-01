import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.data_manager import DataManager
import json

dm = DataManager()
print(f"Key path: {dm.key_path}")
print(f"Settings path: {dm.settings_path}")

# Save a test key
dm.save_configuration("Test Provider", {"Test Provider": "sk-TEST-KEY-12345"})

# Read file raw
with open(dm.settings_path, 'r') as f:
    content = json.load(f)

print("Raw content of settings.json:")
print(json.dumps(content, indent=2))

# Check if key is encrypted
key_in_file = content["api_keys"]["Test Provider"]
if "sk-TEST-KEY" in key_in_file:
    print("FAIL: Key is in CLEAR TEXT")
else:
    print("SUCCESS: Key is ENCRYPTED")
