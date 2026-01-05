import json
import os
import uuid
import datetime
from typing import List, Dict, Any, Optional
from cryptography.fernet import Fernet

from utils.resource_handler import get_writable_path

DATA_FILE = "assistants.json"
SETTINGS_FILE = "settings.json"
KEY_FILE = ".secret.key"
DOC_CONVERSATIONS_FILE = "doc_conversations.json"
PROFILES_FILE = "profiles.json"

class DataManager:
    def __init__(self):
        # Use get_writable_path to ensure files are stored next to the exe or script
        self.filepath = get_writable_path(DATA_FILE)
        self.settings_path = get_writable_path(SETTINGS_FILE)
        self.key_path = get_writable_path(KEY_FILE)
        self.profiles_path = get_writable_path(PROFILES_FILE)
        
        # New structured directory for conversations
        self.conv_root = get_writable_path("conversations")
        self.doc_conv_dir = os.path.join(self.conv_root, "doc_analyst")
        self.assistants_conv_dir = os.path.join(self.conv_root, "assistants")
        
        # Legacy support/migration
        self.old_doc_conversations_path = get_writable_path(DOC_CONVERSATIONS_FILE)
        self.doc_conversations_path = os.path.join(self.doc_conv_dir, DOC_CONVERSATIONS_FILE)
        
        self._load_or_create_key()
        self._ensure_dirs_exist()
        self._migrate_data()
        self._ensure_files_exist()

    def _ensure_dirs_exist(self):
        """Creates the dedicated directory structure for conversations."""
        os.makedirs(self.conv_root, exist_ok=True)
        os.makedirs(self.doc_conv_dir, exist_ok=True)
        os.makedirs(self.assistants_conv_dir, exist_ok=True)
        # Create other placeholders if needed
        for module in ["scraping", "financial", "data_viz"]:
            os.makedirs(os.path.join(self.conv_root, module), exist_ok=True)

    def _migrate_data(self):
        """Migrates data from old root location to new structured subdirectories."""
        # 1. Migrate doc_conversations.json
        if os.path.exists(self.old_doc_conversations_path) and not os.path.exists(self.doc_conversations_path):
            try:
                import shutil
                shutil.move(self.old_doc_conversations_path, self.doc_conversations_path)
                print(f"DEBUG: Migrated {DOC_CONVERSATIONS_FILE} to {self.doc_conversations_path}")
            except Exception as e:
                print(f"Error migrating doc conversations: {e}")

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
        if not os.path.exists(self.doc_conversations_path):
            with open(self.doc_conversations_path, 'w') as f:
                json.dump([], f)
        if not os.path.exists(self.profiles_path):
            with open(self.profiles_path, 'w') as f:
                json.dump([], f)

    def get_all_assistants(self):
        with open(self.filepath, 'r') as f:
            return json.load(f)

    def save_assistant(self, name, description, role="", context="", objective="", limits="", response_format="", target_url="", url_instructions="", provider="", scraping_solution="scrapegraphai", profile_id=None, use_profile=False):
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
            profile_id: ID du profil à utiliser (optionnel)
            use_profile: Activer/désactiver l'utilisation du profil
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
            "profile_id": profile_id,
            "use_profile": use_profile,
            "status": "stopped"  # stopped, running
        }
        assistants.append(new_assistant)
        self._save_to_file(assistants)
        return new_assistant

    def update_assistant(self, assistant_id, name=None, description=None, role=None, 
                        context=None, objective=None, limits=None, response_format=None, target_url=None, url_instructions=None, provider=None, scraping_solution=None, profile_id=None, use_profile=None):
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
            profile_id: ID du profil (optionnel)
            use_profile: Activer/désactiver le profil (optionnel)
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
                if profile_id is not None:
                    assistant["profile_id"] = profile_id
                if use_profile is not None:
                    assistant["use_profile"] = use_profile
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

    # --- Profile Management ---

    def get_all_profiles(self) -> List[Dict[str, Any]]:
        """Récupère tous les profils."""
        try:
            with open(self.profiles_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []

    def save_profile(self, name: str, description: str, role: str = "", context: str = "", 
                     objective: str = "", limits: str = "", response_format: str = "") -> Dict[str, Any]:
        """
        Crée un nouveau profil.
        
        Args:
            name: Nom du profil
            description: Description du profil
            role: Rôle par défaut
            context: Contexte par défaut
            objective: Objectif par défaut
            limits: Limites par défaut
            response_format: Format de réponse par défaut
            
        Returns:
            Le profil créé
        """
        profiles = self.get_all_profiles()
        now = datetime.datetime.now().isoformat()
        new_profile = {
            "id": str(uuid.uuid4()),
            "name": name,
            "description": description,
            "role": role,
            "context": context,
            "objective": objective,
            "limits": limits,
            "response_format": response_format,
            "created_at": now,
            "updated_at": now
        }
        profiles.append(new_profile)
        with open(self.profiles_path, 'w', encoding='utf-8') as f:
            json.dump(profiles, f, indent=4)
        return new_profile

    def update_profile(self, profile_id: str, name: Optional[str] = None, 
                       description: Optional[str] = None, role: Optional[str] = None,
                       context: Optional[str] = None, objective: Optional[str] = None,
                       limits: Optional[str] = None, response_format: Optional[str] = None):
        """
        Met à jour un profil existant.
        
        Args:
            profile_id: ID du profil à modifier
            name: Nouveau nom (optionnel)
            description: Nouvelle description (optionnel)
            role: Nouveau rôle (optionnel)
            context: Nouveau contexte (optionnel)
            objective: Nouvel objectif (optionnel)
            limits: Nouvelles limites (optionnel)
            response_format: Nouveau format de réponse (optionnel)
        """
        profiles = self.get_all_profiles()
        for profile in profiles:
            if profile["id"] == profile_id:
                if name is not None:
                    profile["name"] = name
                if description is not None:
                    profile["description"] = description
                if role is not None:
                    profile["role"] = role
                if context is not None:
                    profile["context"] = context
                if objective is not None:
                    profile["objective"] = objective
                if limits is not None:
                    profile["limits"] = limits
                if response_format is not None:
                    profile["response_format"] = response_format
                profile["updated_at"] = datetime.datetime.now().isoformat()
                break
        with open(self.profiles_path, 'w', encoding='utf-8') as f:
            json.dump(profiles, f, indent=4)

    def delete_profile(self, profile_id: str):
        """Supprime un profil."""
        profiles = self.get_all_profiles()
        profiles = [p for p in profiles if p["id"] != profile_id]
        with open(self.profiles_path, 'w', encoding='utf-8') as f:
            json.dump(profiles, f, indent=4)

    def get_profile_by_id(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """Récupère un profil par son ID."""
        profiles = self.get_all_profiles()
        for profile in profiles:
            if profile["id"] == profile_id:
                return profile
        return None

    def get_effective_assistant_config(self, assistant_id: str) -> Dict[str, Any]:
        """
        Retourne la configuration effective d'un assistant en fusionnant
        le profil (si utilisé) avec les surcharges de l'assistant.
        
        Args:
            assistant_id: ID de l'assistant
            
        Returns:
            Configuration complète avec tous les champs
        """
        assistant = self.get_assistant_by_id(assistant_id)
        if not assistant:
            return {}
        
        # Si pas de profil ou profil désactivé, retourner l'assistant tel quel
        if not assistant.get("use_profile") or not assistant.get("profile_id"):
            return assistant
        
        # Récupérer le profil
        profile = self.get_profile_by_id(assistant["profile_id"])
        if not profile:
            # Profil introuvable, retourner l'assistant tel quel
            return assistant
        
        # Fusionner : profil comme base, assistant comme surcharge
        config = assistant.copy()
        for field in ["role", "context", "objective", "limits", "response_format"]:
            # Si le champ de l'assistant est vide, utiliser celui du profil
            if not config.get(field):
                config[field] = profile.get(field, "")
        
        return config

    # ===== MODULE PROFILE MANAGEMENT =====
    
    def get_module_profile(self, module_name: str) -> Optional[str]:
        """Récupère l'ID du profil associé à un module.
        
        Args:
            module_name: Nom du module (ex: 'doc_analyst', 'data_viz')
        
        Returns:
            L'ID du profil ou None si aucun profil n'est associé
        """
        settings = self.get_settings()
        module_profiles = settings.get("module_profiles", {})
        return module_profiles.get(module_name)
    
    def set_module_profile(self, module_name: str, profile_id: Optional[str]) -> None:
        """Associe un profil à un module.
        
        Args:
            module_name: Nom du module (ex: 'doc_analyst', 'data_viz')
            profile_id: ID du profil à associer, ou None pour détacher
        """
        settings = self.get_settings()
        
        if "module_profiles" not in settings:
            settings["module_profiles"] = {}
        
        if profile_id is None:
            # Retirer l'association
            if module_name in settings["module_profiles"]:
                del settings["module_profiles"][module_name]
        else:
            settings["module_profiles"][module_name] = profile_id
        
        # Sauvegarder les settings
        self.save_configuration(
            chat_provider=settings.get("current_provider", ""),
            scrapegraph_provider=settings.get("scrapegraph_provider", ""),
            api_keys=settings.get("api_keys", {}),
            endpoints=settings.get("endpoints", {})
        )
    
    def get_effective_module_config(self, module_name: str) -> Dict[str, str]:
        """Récupère la configuration effective d'un module (avec profil si défini).
        
        Args:
            module_name: Nom du module
        
        Returns:
            Dictionnaire avec les champs: role, context, objective, limits, response_format
            Retourne un dict vide si aucun profil n'est associé
        """
        profile_id = self.get_module_profile(module_name)
        
        if not profile_id:
            return {}
        
        profile = self.get_profile_by_id(profile_id)
        if not profile:
            return {}
        
        return {
            "role": profile.get("role", ""),
            "context": profile.get("context", ""),
            "objective": profile.get("objective", ""),
            "limits": profile.get("limits", ""),
            "response_format": profile.get("response_format", "")
        }

    def get_doc_conversations(self):
        """Retrieves list of document analysis conversations."""
        try:
            with open(self.doc_conversations_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []

    def save_doc_conversation(self, conversation):
        """Saves or updates a document analysis conversation."""
        conversations = self.get_doc_conversations()
        
        # Check if exists and update
        found = False
        for i, c in enumerate(conversations):
            if c["id"] == conversation["id"]:
                conversations[i] = conversation
                found = True
                break
        
        if not found:
            conversations.append(conversation)
            
        with open(self.doc_conversations_path, 'w', encoding='utf-8') as f:
            json.dump(conversations, f, indent=4)

    def delete_doc_conversation(self, conversation_id):
        """Deletes a document analysis conversation."""
        conversations = self.get_doc_conversations()
        conversations = [c for c in conversations if c["id"] != conversation_id]
        with open(self.doc_conversations_path, 'w', encoding='utf-8') as f:
            json.dump(conversations, f, indent=4)

    def update_doc_conversation_title(self, conversation_id, new_title):
        """Updates the title of a specific conversation."""
        conversations = self.get_doc_conversations()
        for c in conversations:
            if c["id"] == conversation_id:
                c["title"] = new_title
                break
        with open(self.doc_conversations_path, 'w', encoding='utf-8') as f:
            json.dump(conversations, f, indent=4)

    # --- Generic Assistant History Management (Multi-Session) ---

    def _get_history_path(self, module: str, assistant_id: str) -> str:
        """Returns the path to the history file for a specific assistant."""
        module_dir = os.path.join(self.conv_root, module)
        os.makedirs(module_dir, exist_ok=True)
        return os.path.join(module_dir, f"history_{assistant_id}.json")

    def get_assistant_conversations(self, module: str, assistant_id: str) -> List[Dict[str, Any]]:
        """Loads all conversations for a specific assistant."""
        path = self._get_history_path(module, assistant_id)
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Migration logic : if it's a list of messages (old format), wrap it in a conversation object
                    if isinstance(data, list) and len(data) > 0 and "role" in data[0]:
                        old_history = data
                        new_format = [{
                            "id": str(uuid.uuid4()),
                            "title": "Ancienne conversation",
                            "updated_at": str(datetime.datetime.now()), # Note: need import datetime
                            "messages": old_history
                        }]
                        # Save converted format immediately
                        self.save_assistant_conversations(module, assistant_id, new_format)
                        return new_format
                        
                    return data if isinstance(data, list) else []
            except Exception as e:
                print(f"Error loading conversations for {assistant_id}: {e}")
                return []
        return []

    def save_assistant_conversations(self, module: str, assistant_id: str, conversations: List[Dict[str, Any]]):
        """Saves all conversations for a specific assistant."""
        path = self._get_history_path(module, assistant_id)
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(conversations, f, indent=4)
        except Exception as e:
            print(f"Error saving conversations for {assistant_id}: {e}")

    def save_assistant_conversation(self, module: str, assistant_id: str, conversation: Dict[str, Any]):
        """Saves or updates a single conversation for a specific assistant."""
        conversations = self.get_assistant_conversations(module, assistant_id)
        
        found = False
        for i, c in enumerate(conversations):
            if c["id"] == conversation["id"]:
                conversations[i] = conversation
                found = True
                break
        
        if not found:
            conversations.append(conversation)
            
        self.save_assistant_conversations(module, assistant_id, conversations)

    def delete_assistant_conversation(self, module: str, assistant_id: str, conversation_id: str):
        """Deletes a specific conversation for an assistant."""
        conversations = self.get_assistant_conversations(module, assistant_id)
        conversations = [c for c in conversations if c["id"] != conversation_id]
        self.save_assistant_conversations(module, assistant_id, conversations)

    def rename_assistant_conversation(self, module: str, assistant_id: str, conversation_id: str, new_title: str):
        """Renames a specific conversation for an assistant."""
        conversations = self.get_assistant_conversations(module, assistant_id)
        for c in conversations:
            if c["id"] == conversation_id:
                c["title"] = new_title
                break
        self.save_assistant_conversations(module, assistant_id, conversations)


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
