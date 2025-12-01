import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
from utils.data_manager import DataManager

dm = DataManager()
settings = dm.get_settings()
print('=== SETTINGS ===')
print(json.dumps(settings, indent=2, ensure_ascii=False))
