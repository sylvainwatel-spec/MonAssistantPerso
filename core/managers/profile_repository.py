import json
import os
import uuid
import datetime
from typing import List, Dict, Any, Optional

from utils.resource_handler import get_writable_path

PROFILES_FILE = "profiles.json"

class ProfileRepository:
    def __init__(self):
        self.filepath = get_writable_path(PROFILES_FILE)
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not os.path.exists(self.filepath):
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump([], f)

    def get_all(self) -> List[Dict[str, Any]]:
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []

    def save_list(self, profiles: List[Dict[str, Any]]):
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(profiles, f, indent=4)

    def create(self, name: str, description: str, **kwargs) -> Dict[str, Any]:
        profiles = self.get_all()
        now = datetime.datetime.now().isoformat()
        new_profile = {
            "id": str(uuid.uuid4()),
            "name": name,
            "description": description,
            "created_at": now,
            "updated_at": now,
            **kwargs
        }
        # Fill defaults for optional fields if not present
        for field in ["role", "context", "objective", "limits", "response_format"]:
            if field not in new_profile:
                new_profile[field] = ""
                
        profiles.append(new_profile)
        self.save_list(profiles)
        return new_profile

    def update(self, profile_id: str, **kwargs):
        profiles = self.get_all()
        for profile in profiles:
            if profile["id"] == profile_id:
                for k, v in kwargs.items():
                    if v is not None:
                        profile[k] = v
                profile["updated_at"] = datetime.datetime.now().isoformat()
                break
        self.save_list(profiles)

    def delete(self, profile_id: str):
        profiles = self.get_all()
        profiles = [p for p in profiles if p["id"] != profile_id]
        self.save_list(profiles)

    def get_by_id(self, profile_id: str) -> Optional[Dict[str, Any]]:
        profiles = self.get_all()
        for profile in profiles:
            if profile["id"] == profile_id:
                return profile
        return None
