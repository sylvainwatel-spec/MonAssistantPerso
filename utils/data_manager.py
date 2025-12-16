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
                    "chat_provider": "OpenAI GPT-4o mini",
                    "scrapegraph_provider": "OpenAI GPT-4o mini",
                    "image_gen_provider": "OpenAI DALL-E 3",
                    "doc_analyst_provider": "OpenAI GPT-4o mini",
                    "api_keys": {},
                    "endpoints": {},
                    "models": {}
                }, f)

    def get_all_assistants(self):
        with open(self.filepath, 'r') as f:
            return json.load(f)

    def save_assistant(self, name, description, role="", context="", objective="", limits="", response_format="", target_url="", url_instructions="", provider="", scraping_solution="scrapegraphai"):
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
            target_url: URL cible pour les recherches
            url_instructions: Instructions pour se connecter et naviguer sur le site cible
            provider: Provider LLM à utiliser
            scraping_solution: Solution de scraping ("scrapegraphai" ou "playwright")
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
            "url_instructions": url_instructions,
            "provider": provider,
            "scraping_solution": scraping_solution,
            "status": "stopped"  # stopped, running
        }
        assistants.append(new_assistant)
        self._save_to_file(assistants)
        return new_assistant

    def update_assistant(self, assistant_id, name=None, description=None, role=None, 
                        context=None, objective=None, limits=None, response_format=None, target_url=None, url_instructions=None, provider=None, scraping_solution=None):
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
            target_url: Nouvelle URL cible (optionnel)
            url_instructions: Nouvelles instructions URL (optionnel)
            provider: Nouveau provider (optionnel)
            scraping_solution: Nouvelle solution de scraping (optionnel)
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
                if url_instructions is not None:
                    assistant["url_instructions"] = url_instructions
                if provider is not None:
                    assistant["provider"] = provider
                if scraping_solution is not None:
                    assistant["scraping_solution"] = scraping_solution
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
        """Load settings from settings.json and decrypt stored API keys.
        
        Automatically migrates old format (current_provider) to new format 
        (chat_provider, scrapegraph_provider).
        """
        try:
            with open(self.settings_path, 'r') as f:
                data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            # Si le fichier est corrompu ou absent, on retourne les valeurs par défaut
            data = {
                "chat_provider": "OpenAI GPT-4o mini",
                "scrapegraph_provider": "OpenAI GPT-4o mini",
                "api_keys": {},
                "endpoints": {},
                "models": {}
            }
            self.save_configuration(
                data.get("chat_provider", "OpenAI GPT-4o mini"), 
                data.get("scrapegraph_provider", "OpenAI GPT-4o mini"),
                data.get("api_keys", {}),
                endpoints=data.get("endpoints", {}),
                models=data.get("models", {}),
                image_gen_provider=data.get("image_gen_provider", "OpenAI DALL-E 3"),
                doc_analyst_provider=data.get("doc_analyst_provider", "OpenAI GPT-4o mini")
            )
            
        # Migration from old format to new format
        if "current_provider" in data and "chat_provider" not in data:
            old_provider = data.pop("current_provider")
            data["chat_provider"] = old_provider
            # Set scrapegraph_provider from old value or default to OpenAI
            if "scrapegraph_provider" not in data:
                data["scrapegraph_provider"] = "OpenAI GPT-4o mini"
            # Save migrated settings
            self.save_configuration(
                data["chat_provider"],
                data["scrapegraph_provider"],
                data.get("api_keys", {}),
                endpoints=data.get("endpoints", {}),
                models=data.get("models", {})
            )
            
        # Décrypter les clés
        if "api_keys" in data:
            for provider, encrypted_key in data["api_keys"].items():
                data["api_keys"][provider] = self._decrypt(encrypted_key)
        return data

    def save_configuration(self, chat_provider, scrapegraph_provider, api_keys, endpoints=None, models=None, scraping_solution=None, visible_mode=None, scraping_browser=None, image_gen_provider=None, doc_analyst_provider=None, **kwargs):
        """
        Sauvegarde la configuration complète : providers, clés API, endpoints et modèles.
        api_keys: {provider_name: clear_text_key}
        endpoints: {provider_name: url} (optionnel)
        models: {provider_name: model_name} (optionnel)
        **kwargs: Autres paramètres à sauvegarder (ex: tracked_stocks)
        """
        # Charger l'existant sans déclencher de récursion
        try:
            with open(self.settings_path, 'r') as f:
                current = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            current = {"api_keys": {}, "endpoints": {}, "models": {}}
        
        # Mise à jour des providers
        current["chat_provider"] = chat_provider
        current["scrapegraph_provider"] = scrapegraph_provider
        if image_gen_provider:
             current["image_gen_provider"] = image_gen_provider
        if doc_analyst_provider:
             current["doc_analyst_provider"] = doc_analyst_provider
        
        # Mise à jour de la solution de scraping si fournie
        if scraping_solution is not None:
            current["scraping_solution"] = scraping_solution
            
        # Mise à jour du mode visible si fourni
        if visible_mode is not None:
            current["visible_mode"] = visible_mode
            
        # Mise à jour du navigateur scraping si fourni
        if scraping_browser is not None:
            current["scraping_browser"] = scraping_browser
        
        # On s'assure que les sections existent
        if "api_keys" not in current:
            current["api_keys"] = {}
        if "endpoints" not in current:
            current["endpoints"] = {}
        if "models" not in current:
            current["models"] = {}

        # Décrypter les clés existantes d'abord
        decrypted_keys = {}
        if "api_keys" in current:
            for provider, encrypted_key in current["api_keys"].items():
                decrypted_keys[provider] = self._decrypt(encrypted_key)
        
        # Mise à jour des clés (en mémoire) - fusionner avec les nouvelles
        for provider, key in api_keys.items():
            decrypted_keys[provider] = key
            
        # Mise à jour des endpoints
        if endpoints:
            for provider, url in endpoints.items():
                current["endpoints"][provider] = url
        
        # Mise à jour des modèles
        if models:
            for provider, model_name in models.items():
                current["models"][provider] = model_name
            
        # Préparation sauvegarde (Encryption pour les clés uniquement)
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
        
        # Ajouter les autres paramètres (kwargs)
        to_save.update(kwargs)
        
        for prov, key in decrypted_keys.items():
            to_save["api_keys"][prov] = self._encrypt(key)
            
        with open(self.settings_path, 'w') as f:
            json.dump(to_save, f, indent=4)

    def save_settings(self, provider, api_key):
        """Deprecated but kept for compatibility if needed, redirects to save_configuration.
        
        Note: This only saves one key at a time and sets the provider as chat_provider.
        """
        current = self.get_settings()
        api_keys = current.get("api_keys", {})
        api_keys[provider] = api_key
        # Keep existing providers or use the new one as chat_provider
        chat_provider = current.get("chat_provider", provider)
        scrapegraph_provider = current.get("scrapegraph_provider", "OpenAI GPT-4o mini")
        self.save_configuration(chat_provider, scrapegraph_provider, api_keys)
