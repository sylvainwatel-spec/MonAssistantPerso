import json
import os
import uuid
from cryptography.fernet import Fernet

DATA_FILE = "assistants.json"
SETTINGS_FILE = "settings.json"
KEY_FILE = ".secret.key"

class DataManager:
    def __init__(self):
        # Paths are relative to the project root (one level up from utils)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.filepath = os.path.join(base_dir, DATA_FILE)
        self.settings_path = os.path.join(base_dir, SETTINGS_FILE)
        self.key_path = os.path.join(base_dir, KEY_FILE)
        
        self._load_or_create_key()
        self._ensure_files_exist()

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

    def _ensure_files_exist(self):
        if not os.path.exists(self.filepath):
            with open(self.filepath, 'w') as f:
                json.dump([], f)
        if not os.path.exists(self.settings_path):
            with open(self.settings_path, 'w') as f:
                json.dump({
                    "current_provider": "OpenAI GPT-4o mini",
                    "api_keys": {}
                }, f)

    def get_all_assistants(self):
        with open(self.filepath, 'r') as f:
            return json.load(f)

    def save_assistant(self, name, description):
        assistants = self.get_all_assistants()
        new_assistant = {
            "id": str(uuid.uuid4()),
            "name": name,
            "description": description,
            "status": "stopped"  # stopped, running
        }
        assistants.append(new_assistant)
        self._save_to_file(assistants)
        return new_assistant

    def update_status(self, assistant_id, new_status):
        assistants = self.get_all_assistants()
        for assistant in assistants:
            if assistant["id"] == assistant_id:
                assistant["status"] = new_status
                break
        self._save_to_file(assistants)

    def delete_assistant(self, assistant_id):
        assistants = self.get_all_assistants()
        assistants = [a for a in assistants if a["id"] != assistant_id]
        self._save_to_file(assistants)

    def _save_to_file(self, data):
        with open(self.filepath, 'w') as f:
            json.dump(data, f, indent=4)

    def get_settings(self):
        try:
            with open(self.settings_path, 'r') as f:
                data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            # Si le fichier est corrompu ou absent, on retourne les valeurs par défaut
            # et on force une sauvegarde pour réparer le fichier
            data = {
                "current_provider": "OpenAI GPT-4o mini",
                "api_keys": {}
            }
            self.save_configuration(data["current_provider"], data["api_keys"])
            
        # Décrypter les clés
        if "api_keys" in data:
            for provider, encrypted_key in data["api_keys"].items():
                data["api_keys"][provider] = self._decrypt(encrypted_key)
        return data

    def save_configuration(self, active_provider, api_keys):
        """
        Sauvegarde la configuration complète : provider actif et toutes les clés API.
        api_keys est un dictionnaire {provider_name: clear_text_key}
        """
        # Charger l'existant pour ne pas perdre d'autres infos potentielles
        current = self.get_settings()
        
        # Mise à jour
        current["current_provider"] = active_provider
        
        # On s'assure que la section api_keys existe
        if "api_keys" not in current:
            current["api_keys"] = {}

        # Mise à jour des clés (en mémoire)
        for provider, key in api_keys.items():
            current["api_keys"][provider] = key
            
        # Préparation sauvegarde (Encryption)
        to_save = {
            "current_provider": current["current_provider"],
            "api_keys": {}
        }
        
        for prov, key in current["api_keys"].items():
            to_save["api_keys"][prov] = self._encrypt(key)
            
        with open(self.settings_path, 'w') as f:
            json.dump(to_save, f, indent=4)

    def save_settings(self, provider, api_key):
        # Deprecated but kept for compatibility if needed, redirects to save_configuration
        # Note: This only saves one key at a time.
        current = self.get_settings()
        api_keys = current.get("api_keys", {})
        api_keys[provider] = api_key
        self.save_configuration(provider, api_keys)
