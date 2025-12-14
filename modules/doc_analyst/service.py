import os
from typing import Tuple, Dict, Any, List
from pypdf import PdfReader
from core.services.llm_service import LLMService

class DocumentAnalysisService:
    """Service for analyzing documents."""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager

    def extract_text(self, file_path: str) -> Tuple[bool, str]:
        """Extract text from a file (PDF or TXT)."""
        try:
            if not os.path.exists(file_path):
                return False, "Fichier non trouvé"
            
            ext = os.path.splitext(file_path)[1].lower()
            
            if ext == '.pdf':
                reader = PdfReader(file_path)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return True, text
            elif ext == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                return True, text
            else:
                return False, f"Format {ext} non supporté (PDF et TXT uniquement)."
                
        except Exception as e:
            return False, f"Erreur de lecture: {str(e)}"

    def chat_with_document(self, document_context: str, user_question: str, history: List[Dict[str, str]], provider: str) -> Tuple[bool, str]:
        """
        Send context + history + question to LLM.
        Basic RAG-lite (Context Stuffing).
        """
        settings = self.data_manager.get_settings()
        api_keys = settings.get("api_keys", {})
        
        # Mapping friendly names to HF Model IDs
        hf_mapping = {
            "Qwen 2.5 72B (Hugging Face)": "Qwen/Qwen2.5-72B-Instruct"
        }
        
        target_model = None
        kwargs = {}
        
        # Check if provider is one of our custom HF mappings
        if provider in hf_mapping:
            # Use the generic HF key
            api_key = api_keys.get("Hugging Face (Mistral/Mixtral)")
            target_model = hf_mapping[provider]
            # Override provider name for LLMService routing
            actual_provider = "Hugging Face" 
            kwargs['model'] = target_model
        else:
            # Fallback for standard providers (legacy support or if expanded later)
            api_key = api_keys.get(provider)
            actual_provider = provider

        # Handle IAKA/ScrapeGraph special cases or endpoint lookup
        if "IAKA" in actual_provider:
            endpoints = settings.get("endpoints", {})
            kwargs['base_url'] = endpoints.get(provider)
            # Find model name if stored
            models = settings.get("models", {})
            if models.get(provider):
                kwargs['model'] = models.get(provider)

        if not api_key:
            return False, f"Clé API non trouvée pour {provider}."

        # Construct Prompt
        system_prompt = f"""Tu es un analyste de documents expert.
Voici le contenu du document que tu dois analyser :
---
{document_context[:20000]} 
---
(Le document peut être tronqué s'il est trop long)

Réponds aux questions de l'utilisateur en te basant UNIQUEMENT sur ce document. Si la réponse n'est pas dans le document, dis-le."""

        # Prepare messages
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history)
        messages.append({"role": "user", "content": user_question})

        # Call LLM Service
        return LLMService.generate_response(actual_provider, api_key, messages, **kwargs)
