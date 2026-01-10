import json
import os
from cryptography.fernet import Fernet
from typing import Dict, Any, Optional

from utils.resource_handler import get_writable_path

SETTINGS_FILE = "settings.json"
KEY_FILE = ".secret.key"

class SettingsManager:
    def __init__(self):
        self.settings_path = get_writable_path(SETTINGS_FILE)
        self.key_path = get_writable_path(KEY_FILE)
        self.key = None
        self.cipher = None
        
        self._load_or_create_key()
        self._ensure_settings_exist()

    def _load_or_create_key(self):
        if os.path.exists(self.key_path):
            with open(self.key_path, 'rb') as kf:
                self.key = kf.read()
        else:
            self.key = Fernet.generate_key()
            with open(self.key_path, 'wb') as kf:
                kf.write(self.key)
        self.cipher = Fernet(self.key)

    def _encrypt(self, text):
        if not text: return ""
        return self.cipher.encrypt(text.encode()).decode()

    def _decrypt(self, token):
        if not token: return ""
        try:
            return self.cipher.decrypt(token.encode()).decode()
        except:
            return ""

    def _ensure_settings_exist(self):
        if not os.path.exists(self.settings_path):
            with open(self.settings_path, 'w') as f:
                json.dump({
                    "chat_provider": "OpenAI GPT-4o mini",
                    "scrapegraph_provider": "OpenAI GPT-4o mini",
                    "image_gen_provider": "OpenAI DALL-E 3",
                    "doc_analyst_provider": "OpenAI GPT-4o mini",
                    "api_keys": {},
                    "endpoints": {},
                    "models": {}
                }, f)

    def get_settings(self) -> Dict[str, Any]:
        """Load settings and decrypt keys."""
        try:
            with open(self.settings_path, 'r') as f:
                data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
             # Default
            data = {
                "chat_provider": "OpenAI GPT-4o mini",
                "scrapegraph_provider": "OpenAI GPT-4o mini",
                "api_keys": {},
                "endpoints": {},
                "models": {}
            }
            # Save defaults
            self.save_configuration(
                data.get("chat_provider"), 
                data.get("scrapegraph_provider"),
                {},
            )
            
        # Migration logic (simplified from original DataManager)
        if "current_provider" in data and "chat_provider" not in data:
            data["chat_provider"] = data.pop("current_provider")
            if "scrapegraph_provider" not in data:
                data["scrapegraph_provider"] = "OpenAI GPT-4o mini"
            self.save_configuration(data["chat_provider"], data["scrapegraph_provider"], data.get("api_keys", {}))

        # Decrypt
        if "api_keys" in data:
            for provider, encrypted_key in data["api_keys"].items():
                data["api_keys"][provider] = self._decrypt(encrypted_key)
        return data

    def save_configuration(self, chat_provider, scrapegraph_provider, api_keys, endpoints=None, models=None, scraping_solution=None, visible_mode=None, scraping_browser=None, image_gen_provider=None, doc_analyst_provider=None, **kwargs):
        """Save settings with encryption."""
        try:
            with open(self.settings_path, 'r') as f:
                current = json.load(f)
        except:
            current = {"api_keys": {}, "endpoints": {}, "models": {}}
        
        # Update basics
        current["chat_provider"] = chat_provider
        current["scrapegraph_provider"] = scrapegraph_provider
        if image_gen_provider: current["image_gen_provider"] = image_gen_provider
        if doc_analyst_provider: current["doc_analyst_provider"] = doc_analyst_provider
        if scraping_solution is not None: current["scraping_solution"] = scraping_solution
        if visible_mode is not None: current["visible_mode"] = visible_mode
        if scraping_browser is not None: current["scraping_browser"] = scraping_browser
        
        if "api_keys" not in current: current["api_keys"] = {}
        if "endpoints" not in current: current["endpoints"] = {}
        if "models" not in current: current["models"] = {}

        # Decrypt existing keys to merge
        decrypted_keys = {}
        if "api_keys" in current:
            for provider, encrypted_key in current["api_keys"].items():
                decrypted_keys[provider] = self._decrypt(encrypted_key)
        
        # Merge new keys
        for provider, key in api_keys.items():
            decrypted_keys[provider] = key
        
        # Merge endpoints/models
        if endpoints:
            for p, u in endpoints.items(): current["endpoints"][p] = u
        if models:
            for p, m in models.items(): current["models"][p] = m
            
        # Prepare to save
        to_save = {
            "chat_provider": chat_provider,
            "scrapegraph_provider": scrapegraph_provider,
            "api_keys": {},
            "endpoints": current["endpoints"],
            "models": current["models"],
            "scraping_solution": current.get("scraping_solution", "scrapegraphai"),
            "visible_mode": current.get("visible_mode", False),
            "scraping_browser": current.get("scraping_browser", "firefox"),
            "image_gen_provider": current.get("image_gen_provider", "OpenAI DALL-E 3"),
            "doc_analyst_provider": current.get("doc_analyst_provider", "OpenAI GPT-4o mini")
        }
        to_save.update(kwargs) # Add other kwargs
        
        # Encrypt keys
        for prov, key in decrypted_keys.items():
            to_save["api_keys"][prov] = self._encrypt(key)
            
        with open(self.settings_path, 'w') as f:
            json.dump(to_save, f, indent=4)
