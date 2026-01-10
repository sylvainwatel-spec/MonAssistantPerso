import json
import os
import uuid
from typing import List, Dict, Any, Optional

from utils.resource_handler import get_writable_path

DATA_FILE = "assistants.json"

class AssistantRepository:
    def __init__(self):
        self.filepath = get_writable_path(DATA_FILE)
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not os.path.exists(self.filepath):
            with open(self.filepath, 'w') as f:
                json.dump([], f)

    def get_all(self) -> List[Dict[str, Any]]:
        with open(self.filepath, 'r') as f:
            return json.load(f)

    def save(self, data: List[Dict[str, Any]]):
        with open(self.filepath, 'w') as f:
            json.dump(data, f, indent=4)

    def create(self, **kwargs) -> Dict[str, Any]:
        assistants = self.get_all()
        new_assistant = {
            "id": str(uuid.uuid4()),
            "status": "stopped",
            **kwargs
        }
        # Ensure critical fields exist if not passed
        if "name" not in new_assistant: new_assistant["name"] = "New Assistant"
        
        assistants.append(new_assistant)
        self.save(assistants)
        return new_assistant

    def update(self, assistant_id: str, **kwargs):
        assistants = self.get_all()
        for assistant in assistants:
            if assistant["id"] == assistant_id:
                for k, v in kwargs.items():
                    if v is not None:
                        assistant[k] = v
                break
        self.save(assistants)

    def get_by_id(self, assistant_id: str) -> Optional[Dict[str, Any]]:
        assistants = self.get_all()
        for assistant in assistants:
            if assistant["id"] == assistant_id:
                return assistant
        return None

    def delete(self, assistant_id: str):
        assistants = self.get_all()
        assistants = [a for a in assistants if a["id"] != assistant_id]
        self.save(assistants)
