import json
import os
import uuid
from cryptography.fernet import Fernet

from utils.resource_handler import get_writable_path

DATA_FILE = "assistants.json"
SETTINGS_FILE = "settings.json"
KEY_FILE = ".secret.key"

class DataManager:
    def __init__(self):
        # Use get_writable_path to ensure files are stored next to the exe or script
        self.filepath = get_writable_path(DATA_FILE)
        self.settings_path = get_writable_path(SETTINGS_FILE)
        self.key_path = get_writable_path(KEY_FILE)
        
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

    def save_assistant(self, name, description, role="", context="", objective="", limits="", response_format="", target_url="", provider=""):
        """
        Sauvegarde un nouvel assistant avec tous ses champs.
        
        Args:
            name: Nom de l'assistant
            description: Description courte
            role: Rôle de l'assistant
            context: Contexte d'utilisation
            objective: Objectif principal
            limits: Limites et restrictions
            response_format: Format de réponse souhaité
            response_format: Format de réponse souhaité
            target_url: URL cible pour les recherches
            provider: Provider LLM à utiliser
        """
        assistants = self.get_all_assistants()
        new_assistant = {
            "id": str(uuid.uuid4()),
            "name": name,
            "description": description,
            "role": role,
            "context": context,
            "objective": objective,
            "limits": limits,
            "response_format": response_format,
            "target_url": target_url,
            "provider": provider,
            "status": "stopped"  # stopped, running
        }
        assistants.append(new_assistant)
        self._save_to_file(assistants)
        return new_assistant

    def update_assistant(self, assistant_id, name=None, description=None, role=None, 
                        context=None, objective=None, limits=None, response_format=None, target_url=None, provider=None):
        """
        Met à jour un assistant existant.
        
        Args:
            assistant_id: ID de l'assistant à modifier
            name: Nouveau nom (optionnel)
            description: Nouvelle description (optionnel)
            role: Nouveau rôle (optionnel)
            context: Nouveau contexte (optionnel)
            objective: Nouvel objectif (optionnel)
            limits: Nouvelles limites (optionnel)
            response_format: Nouveau format de réponse (optionnel)
            response_format: Nouveau format de réponse (optionnel)
            target_url: Nouvelle URL cible (optionnel)
            provider: Nouveau provider (optionnel)
        """
        assistants = self.get_all_assistants()
        for assistant in assistants:
            if assistant["id"] == assistant_id:
                if name is not None:
                    assistant["name"] = name
                if description is not None:
                    assistant["description"] = description
                if role is not None:
                    assistant["role"] = role
                if context is not None:
                    assistant["context"] = context
                if objective is not None:
                    assistant["objective"] = objective
                if limits is not None:
                    assistant["limits"] = limits
                if response_format is not None:
                    assistant["response_format"] = response_format
                if target_url is not None:
                    assistant["target_url"] = target_url
                if provider is not None:
                    assistant["provider"] = provider
                break
        self._save_to_file(assistants)

    def get_assistant_by_id(self, assistant_id):
        """Récupère un assistant par son ID."""
        assistants = self.get_all_assistants()
        for assistant in assistants:
            if assistant["id"] == assistant_id:
                return assistant
        return None

    def update_status(self, assistant_id, new_status):
        """Met à jour le statut d'un assistant."""
        assistants = self.get_all_assistants()
        for assistant in assistants:
            if assistant["id"] == assistant_id:
                assistant["status"] = new_status
                break
        self._save_to_file(assistants)

    def delete_assistant(self, assistant_id):
        """Supprime un assistant."""
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
