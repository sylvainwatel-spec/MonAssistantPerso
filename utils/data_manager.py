import json
import os
import uuid
import datetime
from typing import List, Dict, Any, Optional
from core.managers.settings_manager import SettingsManager
from core.managers.assistant_repository import AssistantRepository
from core.managers.profile_repository import ProfileRepository
from utils.resource_handler import get_writable_path

# Keep constants for backward compatibility if imported elsewhere
DATA_FILE = "assistants.json"
SETTINGS_FILE = "settings.json"
KEY_FILE = ".secret.key"
DOC_CONVERSATIONS_FILE = "doc_conversations.json"
PROFILES_FILE = "profiles.json"
KNOWLEDGE_BASES_FILE = "knowledge_bases.json"

class DataManager:
    """
    Facade class that delegates to specialized managers/repositories.
    Maintains the original API for backward compatibility.
    """
    def __init__(self):
        # Initialize sub-managers
        self.settings_manager = SettingsManager()
        self.assistant_repo = AssistantRepository()
        self.profile_repo = ProfileRepository()
        
        # Paths still used directly until we move everything
        self.knowledge_bases_path = get_writable_path(KNOWLEDGE_BASES_FILE)
        self.conv_root = get_writable_path("conversations")
        self.doc_conv_dir = os.path.join(self.conv_root, "doc_analyst")
        self.assistants_conv_dir = os.path.join(self.conv_root, "assistants")
        self.vector_db_root = get_writable_path("vector_databases")
        
        self.old_doc_conversations_path = get_writable_path(DOC_CONVERSATIONS_FILE)
        self.doc_conversations_path = os.path.join(self.doc_conv_dir, DOC_CONVERSATIONS_FILE)
        
        self._ensure_dirs_exist()
        self._migrate_data()
        self._ensure_files_exist()

    def _ensure_dirs_exist(self):
        os.makedirs(self.conv_root, exist_ok=True)
        os.makedirs(self.doc_conv_dir, exist_ok=True)
        os.makedirs(self.assistants_conv_dir, exist_ok=True)
        os.makedirs(self.vector_db_root, exist_ok=True)
        for module in ["scraping", "financial", "data_viz"]:
            os.makedirs(os.path.join(self.conv_root, module), exist_ok=True)

    def _migrate_data(self):
        if os.path.exists(self.old_doc_conversations_path) and not os.path.exists(self.doc_conversations_path):
            try:
                import shutil
                shutil.move(self.old_doc_conversations_path, self.doc_conversations_path)
            except Exception as e:
                print(f"Error migrating doc conversations: {e}")

    def _ensure_files_exist(self):
        if not os.path.exists(self.doc_conversations_path):
            with open(self.doc_conversations_path, 'w') as f:
                json.dump([], f)
        if not os.path.exists(self.knowledge_bases_path):
            with open(self.knowledge_bases_path, 'w') as f:
                json.dump([], f)

    # --- Delegation: Settings ---
    def get_settings(self):
        return self.settings_manager.get_settings()

    def save_configuration(self, *args, **kwargs):
        return self.settings_manager.save_configuration(*args, **kwargs)

    def save_settings(self, provider, api_key):
        """Deprecated but kept for compatibility."""
        current = self.get_settings()
        api_keys = current.get("api_keys", {})
        api_keys[provider] = api_key
        chat_provider = current.get("chat_provider", provider)
        scrapegraph_provider = current.get("scrapegraph_provider", "OpenAI GPT-4o mini")
        self.save_configuration(chat_provider, scrapegraph_provider, api_keys)

    # --- Delegation: Assistants ---
    def get_all_assistants(self):
        return self.assistant_repo.get_all()

    def save_assistant(self, name, description, role="", context="", objective="", limits="", response_format="", target_url="", url_instructions="", provider="", scraping_solution="scrapegraphai", profile_id=None, use_profile=False, knowledge_base_id=None):
        return self.assistant_repo.create(
            name=name, description=description, role=role, context=context, objective=objective,
            limits=limits, response_format=response_format, target_url=target_url,
            url_instructions=url_instructions, provider=provider, scraping_solution=scraping_solution,
            profile_id=profile_id, use_profile=use_profile, knowledge_base_id=knowledge_base_id
        )

    def update_assistant(self, assistant_id, **kwargs):
        self.assistant_repo.update(assistant_id, **kwargs)

    def get_assistant_by_id(self, assistant_id):
        return self.assistant_repo.get_by_id(assistant_id)

    def update_status(self, assistant_id, new_status):
        self.assistant_repo.update(assistant_id, status=new_status)

    def delete_assistant(self, assistant_id):
        self.assistant_repo.delete(assistant_id)

    # --- Delegation: Profiles ---
    def get_all_profiles(self) -> List[Dict[str, Any]]:
        return self.profile_repo.get_all()

    def save_profile(self, name: str, description: str, role: str = "", context: str = "", 
                     objective: str = "", limits: str = "", response_format: str = "") -> Dict[str, Any]:
        return self.profile_repo.create(name, description, role=role, context=context, 
                                      objective=objective, limits=limits, response_format=response_format)

    def update_profile(self, profile_id: str, **kwargs):
        self.profile_repo.update(profile_id, **kwargs)

    def delete_profile(self, profile_id: str):
        self.profile_repo.delete(profile_id)

    def get_profile_by_id(self, profile_id: str) -> Optional[Dict[str, Any]]:
        return self.profile_repo.get_by_id(profile_id)

    # --- Business Logic: Effective Config (Kept here or could move to AssistantRepo/Service) ---
    def get_effective_assistant_config(self, assistant_id: str) -> Dict[str, Any]:
        assistant = self.get_assistant_by_id(assistant_id)
        if not assistant: return {}
        if not assistant.get("use_profile") or not assistant.get("profile_id"):
            return assistant
        
        profile = self.get_profile_by_id(assistant["profile_id"])
        if not profile: return assistant
        
        config = assistant.copy()
        for field in ["role", "context", "objective", "limits", "response_format"]:
            if not config.get(field):
                config[field] = profile.get(field, "")
        return config

    # --- Module Profile Management (Uses SettingsManager) ---
    def get_module_profile(self, module_name: str) -> Optional[str]:
        settings = self.get_settings()
        return settings.get("module_profiles", {}).get(module_name)
    
    def set_module_profile(self, module_name: str, profile_id: Optional[str]) -> None:
        settings = self.get_settings()
        if "module_profiles" not in settings: settings["module_profiles"] = {}
        
        if profile_id is None:
            if module_name in settings["module_profiles"]:
                del settings["module_profiles"][module_name]
        else:
            settings["module_profiles"][module_name] = profile_id
            
        # Re-save settings
        self.save_configuration(
            chat_provider=settings.get("chat_provider", ""),
            scrapegraph_provider=settings.get("scrapegraph_provider", ""),
            api_keys=settings.get("api_keys", {}),
            endpoints=settings.get("endpoints", {}),
            module_profiles=settings["module_profiles"]
        )
    
    def get_effective_module_config(self, module_name: str) -> Dict[str, str]:
        profile_id = self.get_module_profile(module_name)
        if not profile_id: return {}
        profile = self.get_profile_by_id(profile_id)
        if not profile: return {}
        return {
            "role": profile.get("role", ""),
            "context": profile.get("context", ""),
            "objective": profile.get("objective", ""),
            "limits": profile.get("limits", ""),
            "response_format": profile.get("response_format", "")
        }

    # --- Doc Conversations (To be refactored similar to above but kept here for now) ---
    def get_doc_conversations(self):
        try:
            with open(self.doc_conversations_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception: return []

    def save_doc_conversation(self, conversation):
        conversations = self.get_doc_conversations()
        found = False
        for i, c in enumerate(conversations):
            if c["id"] == conversation["id"]:
                conversations[i] = conversation
                found = True
                break
        if not found: conversations.append(conversation)
        with open(self.doc_conversations_path, 'w', encoding='utf-8') as f:
            json.dump(conversations, f, indent=4)

    def delete_doc_conversation(self, conversation_id):
        conversations = self.get_doc_conversations()
        conversations = [c for c in conversations if c["id"] != conversation_id]
        with open(self.doc_conversations_path, 'w', encoding='utf-8') as f:
            json.dump(conversations, f, indent=4)

    def update_doc_conversation_title(self, conversation_id, new_title):
        conversations = self.get_doc_conversations()
        for c in conversations:
            if c["id"] == conversation_id:
                c["title"] = new_title
                break
        with open(self.doc_conversations_path, 'w', encoding='utf-8') as f:
            json.dump(conversations, f, indent=4)

    # --- Generic Assistant History Management ---
    def _get_history_path(self, module: str, assistant_id: str) -> str:
        module_dir = os.path.join(self.conv_root, module)
        os.makedirs(module_dir, exist_ok=True)
        return os.path.join(module_dir, f"history_{assistant_id}.json")

    def get_assistant_conversations(self, module: str, assistant_id: str) -> List[Dict[str, Any]]:
        path = self._get_history_path(module, assistant_id)
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list) and len(data) > 0 and "role" in data[0]:
                        new_format = [{
                            "id": str(uuid.uuid4()),
                            "title": "Ancienne conversation",
                            "updated_at": str(datetime.datetime.now()),
                            "messages": data
                        }]
                        self.save_assistant_conversations(module, assistant_id, new_format)
                        return new_format
                    return data if isinstance(data, list) else []
            except Exception as e:
                print(f"Error loading conversations for {assistant_id}: {e}")
                return []
        return []

    def save_assistant_conversations(self, module: str, assistant_id: str, conversations: List[Dict[str, Any]]):
        path = self._get_history_path(module, assistant_id)
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(conversations, f, indent=4)
        except Exception as e:
            print(f"Error saving conversations for {assistant_id}: {e}")

    def save_assistant_conversation(self, module: str, assistant_id: str, conversation: Dict[str, Any]):
        conversations = self.get_assistant_conversations(module, assistant_id)
        found = False
        for i, c in enumerate(conversations):
            if c["id"] == conversation["id"]:
                conversations[i] = conversation
                found = True
                break
        if not found: conversations.append(conversation)
        self.save_assistant_conversations(module, assistant_id, conversations)

    def delete_assistant_conversation(self, module: str, assistant_id: str, conversation_id: str):
        conversations = self.get_assistant_conversations(module, assistant_id)
        conversations = [c for c in conversations if c["id"] != conversation_id]
        self.save_assistant_conversations(module, assistant_id, conversations)

    def rename_assistant_conversation(self, module: str, assistant_id: str, conversation_id: str, new_title: str):
        conversations = self.get_assistant_conversations(module, assistant_id)
        for c in conversations:
            if c["id"] == conversation_id:
                c["title"] = new_title
                break
        self.save_assistant_conversations(module, assistant_id, conversations)
        
    # --- Knowledge Base Management (Partial moved logic could improve this too, but leaving for now) ---
    def get_all_knowledge_bases(self) -> List[Dict[str, Any]]:
        try:
            with open(self.knowledge_bases_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception: return []

    def save_knowledge_base(self, name: str, description: str) -> Dict[str, Any]:
        knowledge_bases = self.get_all_knowledge_bases()
        now = datetime.datetime.now().isoformat()
        new_kb = {
            "id": str(uuid.uuid4()), "name": name, "description": description,
            "created_at": now, "updated_at": now, "document_count": 0, "chunk_count": 0
        }
        knowledge_bases.append(new_kb)
        with open(self.knowledge_bases_path, 'w', encoding='utf-8') as f:
            json.dump(knowledge_bases, f, indent=4)
        return new_kb

    def update_knowledge_base(self, kb_id: str, **kwargs) -> None:
        knowledge_bases = self.get_all_knowledge_bases()
        for kb in knowledge_bases:
            if kb["id"] == kb_id:
                for k, v in kwargs.items():
                    if v is not None: kb[k] = v
                kb["updated_at"] = datetime.datetime.now().isoformat()
                break
        with open(self.knowledge_bases_path, 'w', encoding='utf-8') as f:
            json.dump(knowledge_bases, f, indent=4)

    def delete_knowledge_base(self, kb_id: str) -> None:
        knowledge_bases = self.get_all_knowledge_bases()
        knowledge_bases = [kb for kb in knowledge_bases if kb["id"] != kb_id]
        with open(self.knowledge_bases_path, 'w', encoding='utf-8') as f:
            json.dump(knowledge_bases, f, indent=4)

    def get_knowledge_base_by_id(self, kb_id: str) -> Optional[Dict[str, Any]]:
        knowledge_bases = self.get_all_knowledge_bases()
        for kb in knowledge_bases:
            if kb["id"] == kb_id: return kb
        return None
