"""
Core Client Service for LLM connections.
Handles connection testing and provider management.
"""

from typing import Tuple, Optional, Any, Dict, List

class LLMService:
    """Service for checking connections and generating responses from various LLM providers."""
    
    # --- Generation Methods ---

    @staticmethod
    def generate_openai(api_key: str, messages: List[Dict[str, str]], model: str = "gpt-4o-mini", **kwargs) -> Tuple[bool, str]:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            if not model:
                model = "gpt-4o-mini"
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                **kwargs
            )
            return True, response.choices[0].message.content
        except Exception as e:
            return False, f"Erreur OpenAI: {str(e)}"

    @staticmethod
    def generate_gemini(api_key: str, messages: List[Dict[str, str]], model: str = "gemini-1.5-flash", **kwargs) -> Tuple[bool, str]:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            if not model:
                model = "gemini-1.5-flash"
            model_instance = genai.GenerativeModel(model)
            
            # Convert generic messages to Gemini history format if needed, or simple prompt
            # For simplicity in this v1, connecting last user message
            last_msg = messages[-1]['content']
            
            # TODO: Better history handling
            response = model_instance.generate_content(last_msg)
            return True, response.text
        except Exception as e:
            return False, f"Erreur Gemini: {str(e)}"

    @staticmethod
    def generate_anthropic(api_key: str, messages: List[Dict[str, str]], model: str = "claude-3-opus-20240229", **kwargs) -> Tuple[bool, str]:
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=api_key)
            
            # Extract system message if present
            system_prompt = None
            filtered_messages = []
            for msg in messages:
                if msg['role'] == 'system':
                    system_prompt = msg['content']
                else:
                    filtered_messages.append(msg)
            
                    filtered_messages.append(msg)
            
            if not model:
                model = "claude-3-opus-20240229"

            create_args = {
                "model": model,
                "messages": filtered_messages,
                "max_tokens": 4000
            }
            if system_prompt:
                create_args["system"] = system_prompt
                
            response = client.messages.create(**create_args)
            return True, response.content[0].text
        except Exception as e:
            return False, f"Erreur Anthropic: {str(e)}"

    @staticmethod
    def generate_groq(api_key: str, messages: List[Dict[str, str]], model: str = "llama-3.1-8b-instant", **kwargs) -> Tuple[bool, str]:
        try:
            from groq import Groq
            # Client doesn't need base_url usually, but if needed it typically goes in constructor
            # For now just remove it from kwargs to avoid the error
            kwargs.pop('base_url', None)
            
            if not model or model == "llama3-8b-8192":
                model = "llama-3.1-8b-instant"

            client = Groq(api_key=api_key)
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                **kwargs
            )
            return True, response.choices[0].message.content
        except Exception as e:
            return False, f"Erreur Groq: {str(e)}"

    @staticmethod
    def generate_mistral(api_key: str, messages: List[Dict[str, str]], model: str = "mistral-small-latest", **kwargs) -> Tuple[bool, str]:
        try:
            from mistralai import Mistral
            # Remove base_url if present
            kwargs.pop('base_url', None)
            
            if not model:
                model = "mistral-small-latest"

            client = Mistral(api_key=api_key)
            response = client.chat.complete(
                model=model,
                messages=messages,
                **kwargs
            )
            return True, response.choices[0].message.content
        except Exception as e:
            return False, f"Erreur Mistral: {str(e)}"

    @staticmethod
    def generate_huggingface(api_key: str, messages: List[Dict[str, str]], model: str = "mistralai/Mistral-7B-Instruct-v0.2", **kwargs) -> Tuple[bool, str]:
        try:
            from huggingface_hub import InferenceClient
            client = InferenceClient(token=api_key)
            
            # Default model if none provided or it's generic
            if not model or model == "default":
                model = "mistralai/Mistral-7B-Instruct-v0.2"
                
            response = client.chat_completion(
                messages=messages,
                model=model,
                max_tokens=kwargs.get('max_tokens', 4000),
                temperature=kwargs.get('temperature', 0.7)
            )
            return True, response.choices[0].message.content
        except Exception as e:
             return False, f"Erreur Hugging Face: {str(e)}"

    @staticmethod
    def generate_openai_compatible(api_key: str, messages: List[Dict[str, str]], base_url: str, model: str = "default", **kwargs) -> Tuple[bool, str]:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key, base_url=base_url)
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                **kwargs
            )
            return True, response.choices[0].message.content
        except Exception as e:
            return False, f"Erreur Compatible OpenAI: {str(e)}"
            
    # --- Testing Methods (Existing) ---
    
    @staticmethod
    def test_openai(api_key: str) -> Tuple[bool, str]:
        """
        Test de connexion à OpenAI GPT.
        
        Args:
            api_key: Clé API OpenAI
            
        Returns:
            Tuple (succès: bool, message: str)
        """
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=api_key)
            
            # Requête minimale pour vérifier la clé
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5,
                n=1,
                temperature=0,
            )
            
            content = response.choices[0].message.content if response.choices else ""
            return True, f"Connexion réussie à OpenAI !\nModèle: gpt-3.5-turbo\nRéponse: {content}"
            
        except Exception as e:
            return False, f"Erreur OpenAI: {str(e)}"
    
    @staticmethod
    def test_google_gemini(api_key: str) -> Tuple[bool, str]:
        """
        Test de connexion à Google Gemini.
        
        Args:
            api_key: Clé API Google
            
        Returns:
            Tuple (succès: bool, message: str)
        """
        try:
            import google.generativeai as genai
            
            # Configuration de l'API
            genai.configure(api_key=api_key)
            
            # Liste des modèles à tester
            # On privilégie les modèles 1.5 et 2.0 qui sont les plus récents et performants
            models_to_test = [
                "gemini-2.0-flash-exp",
                "gemini-1.5-flash",
                "gemini-1.5-pro",
                "gemini-pro"
            ]
            
            last_error = None
            
            # Essayer chaque modèle jusqu'à ce qu'un fonctionne
            for model_name in models_to_test:
                try:
                    # Créer le modèle
                    model = genai.GenerativeModel(model_name)
                    
                    # Test avec une requête simple
                    response = model.generate_content("Hello")
                    
                    # Extraire la réponse
                    response_text = response.text if hasattr(response, 'text') else str(response)
                    
                    # Nettoyer le nom du modèle pour l'affichage
                    display_name = model_name.replace('models/', '')
                    
                    return True, f"Connexion réussie à Google Gemini !\nModèle: {display_name}\nRéponse: {response_text[:50]}..."
                    
                except Exception as e:
                    error_msg = str(e)
                    last_error = error_msg
                    
                    # Si c'est une erreur de quota, on arrête d'essayer immédiatement
                    if '429' in error_msg or 'quota' in error_msg.lower() or 'resource_exhausted' in error_msg.lower():
                        return False, f"Quota dépassé pour Google Gemini.\n\nAttendez quelques minutes ou utilisez un autre provider.\n\nConsultez vos quotas: https://aistudio.google.com/apikey"
                    
                    # Si c'est une erreur d'authentification, on arrête immédiatement
                    if '401' in error_msg or '403' in error_msg or 'invalid api key' in error_msg.lower():
                        return False, f"Clé API invalide ou non autorisée.\n\nVérifiez votre clé API sur https://aistudio.google.com/apikey\n\nDétails: {error_msg}"
                    
                    # Pour les autres erreurs, on continue avec le modèle suivant
                    continue
            
            # Si aucun modèle n'a fonctionné
            import google.generativeai as genai_pkg
            version_info = getattr(genai_pkg, '__version__', 'inconnue')
            
            return False, f"Impossible de se connecter à Google Gemini.\n\nLa clé API semble valide mais aucun des modèles testés ({', '.join(models_to_test)}) n'est accessible.\n\nVersion librairie: {version_info}\n\nDernière erreur: {last_error[:200]}\n\nVérifiez que votre clé a les bonnes permissions sur:\nhttps://aistudio.google.com/apikey"
            
        except Exception as e:
            return False, f"Erreur Google Gemini: {str(e)}"
    
    @staticmethod
    def test_anthropic_claude(api_key: str) -> Tuple[bool, str]:
        """
        Test de connexion à Anthropic Claude.
        
        Args:
            api_key: Clé API Anthropic
            
        Returns:
            Tuple (succès: bool, message: str)
        """
        try:
            from anthropic import Anthropic
            
            client = Anthropic(api_key=api_key)
            
            # Requête minimale pour vérifier la clé
            response = client.messages.create(
                model="claude-opus-4-20250514",
                max_tokens=10,
                messages=[{"role": "user", "content": "Hello"}]
            )
            
            content = response.content[0].text if response.content else ""
            return True, f"Connexion réussie à Anthropic Claude !\nModèle: claude-opus-4\nRéponse: {content}"
            
        except Exception as e:
            return False, f"Erreur Anthropic Claude: {str(e)}"
    
    @staticmethod
    def test_groq_llama(api_key: str) -> Tuple[bool, str]:
        """
        Test de connexion à Meta Llama 3 via Groq.
        
        Args:
            api_key: Clé API Groq
            
        Returns:
            Tuple (succès: bool, message: str)
        """
        try:
            from groq import Groq
            
            client = Groq(api_key=api_key)
            
            # Requête minimale pour vérifier la clé
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5,
            )
            
            content = response.choices[0].message.content if response.choices else ""
            return True, f"Connexion réussie à Groq (Llama 3) !\nModèle: llama-3.1-8b-instant\nRéponse: {content}"
            
        except Exception as e:
            return False, f"Erreur Groq/Llama: {str(e)}"
    
    @staticmethod
    def test_mistral(api_key: str) -> Tuple[bool, str]:
        """
        Test de connexion à Mistral AI.
        
        Args:
            api_key: Clé API Mistral
            
        Returns:
            Tuple (succès: bool, message: str)
        """
        try:
            from mistralai import Mistral
            
            client = Mistral(api_key=api_key)
            
            # Requête minimale pour vérifier la clé
            response = client.chat.complete(
                model="mistral-small-latest",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            
            content = response.choices[0].message.content if response.choices else ""
            return True, f"Connexion réussie à Mistral AI !\nModèle: mistral-small\nRéponse: {content}"
            
        except Exception as e:
            return False, f"Erreur Mistral AI: {str(e)}"
    
    @staticmethod
    def test_deepseek(api_key: str) -> Tuple[bool, str]:
        """
        Test de connexion à DeepSeek.
        
        Args:
            api_key: Clé API DeepSeek
            
        Returns:
            Tuple (succès: bool, message: str)
        """
        try:
            from openai import OpenAI
            
            # DeepSeek est compatible avec l'API OpenAI
            client = OpenAI(
                api_key=api_key,
                base_url="https://api.deepseek.com"
            )
            
            # Requête minimale pour vérifier la clé
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5,
            )
            
            content = response.choices[0].message.content if response.choices else ""
            return True, f"Connexion réussie à DeepSeek !\nModèle: deepseek-chat\nRéponse: {content}"
            
        except Exception as e:
            return False, f"Erreur DeepSeek: {str(e)}"

    @staticmethod
    def test_deepseek_vl(api_key: str) -> Tuple[bool, str]:
        """
        Test de connexion à DeepSeek-VL (Vision-Language).
        
        Args:
            api_key: Clé API DeepSeek
            
        Returns:
            Tuple (succès: bool, message: str)
        """
        try:
            from openai import OpenAI
            
            # DeepSeek-VL est compatible avec l'API OpenAI
            client = OpenAI(
                api_key=api_key,
                base_url="https://api.deepseek.com"
            )
            
            # Requête minimale pour vérifier la clé
            response = client.chat.completions.create(
                model="deepseek-vl",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5,
            )
            
            content = response.choices[0].message.content if response.choices else ""
            return True, f"Connexion réussie à DeepSeek-VL !\nModèle: deepseek-vl\nRéponse: {content}"
            
        except Exception as e:
            return False, f"Erreur DeepSeek-VL: {str(e)}"

    @staticmethod
    def test_huggingface(api_key: str) -> Tuple[bool, str]:
        """
        Test de connexion à Hugging Face Inference API.
        
        Args:
            api_key: Token Hugging Face
            
        Returns:
            Tuple (succès: bool, message: str)
        """
        try:
            from huggingface_hub import InferenceClient
            
            client = InferenceClient(token=api_key)
            
            # Test avec un modèle compatible chat_completion
            # Utiliser Qwen2.5 qui est gratuit et supporte chat
            response = client.chat_completion(
                messages=[{"role": "user", "content": "Hello"}],
                model="Qwen/Qwen2.5-72B-Instruct",
                max_tokens=10
            )
            
            content = response.choices[0].message.content if response.choices else ""
            return True, f"Connexion réussie à Hugging Face !\nModèle: Qwen2.5-72B-Instruct\nRéponse: {content[:50]}..."
            
        except Exception as e:
            return False, f"Erreur Hugging Face: {str(e)}"

    @staticmethod
    def test_openai_compatible(api_key: str, base_url: str) -> Tuple[bool, str]:
        """
        Test de connexion à un provider compatible OpenAI (ex: IAKA).
        
        Args:
            api_key: Clé API
            base_url: URL de base de l'API
            
        Returns:
            Tuple (succès: bool, message: str)
        """
        try:
            from openai import OpenAI
            
            if not base_url:
                return False, "URL de base (Endpoint) manquante."
            
            client = OpenAI(
                api_key=api_key,
                base_url=base_url
            )
            
            # Requête minimale pour vérifier la clé
            # On utilise un modèle générique souvent supporté ou on essaie de lister les modèles
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo", # Souvent mappé par défaut, sinon on peut essayer "default"
                    messages=[{"role": "user", "content": "Hello"}],
                    max_tokens=5,
                    temperature=0,
                )
                model_used = "gpt-3.5-turbo (défaut)"
                content = response.choices[0].message.content if response.choices else ""
            except Exception as e:
                # Si le modèle n'existe pas, on essaie de lister les modèles pour en trouver un valide
                try:
                    models = client.models.list()
                    if models.data:
                        first_model = models.data[0].id
                        response = client.chat.completions.create(
                            model=first_model,
                            messages=[{"role": "user", "content": "Hello"}],
                            max_tokens=5,
                            temperature=0,
                        )
                        model_used = first_model
                        content = response.choices[0].message.content if response.choices else ""
                    else:
                        raise e
                except:
                    raise e
            
            return True, f"Connexion réussie au provider compatible OpenAI !\nEndpoint: {base_url}\nModèle: {model_used}\nRéponse: {content}"
            
        except Exception as e:
            return False, f"Erreur Provider Compatible: {str(e)}"

    @staticmethod
    def test_iaka(api_key: str, base_url: str, model_name: str = "mistral-small") -> Tuple[bool, str]:
        """
        Test de connexion au connector IAKA.
        
        Args:
            api_key: Clé API
            base_url: URL de base de l'API (ex: https://iaka-api...)
            model_name: Nom du modèle (défaut: mistral-small)
            
        Returns:
            Tuple (succès: bool, message: str)
        """
        try:
            from openai import OpenAI
            
            if not base_url:
                return False, "URL de base (Endpoint) manquante."
            
            # Construction de l'URL spécifique IAKA
            # Structure : {BASE_URL}/{CODE_MODEL}/v1
            if not model_name:
                model_name = "mistral-small"
            
            # Nettoyage de l'URL de base (retirer le slash final si présent)
            clean_base_url = base_url.rstrip('/')
            
            # Construction de l'URL complète
            full_url = f"{clean_base_url}/{model_name}/v1"
            
            client = OpenAI(
                api_key=api_key,
                base_url=full_url
            )
            
            # Requête simple pour tester
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": "Hello"}],
                temperature=0.1,
                top_p=1,
                max_tokens=5,
                stream=False
            )
            
            content = response.choices[0].message.content if response.choices else ""
            
            return True, f"Connexion réussie à IAKA !\nURL: {full_url}\nModèle: {model_name}\nRéponse: {content}"
            
        except Exception as e:
            return False, f"Erreur IAKA: {str(e)}"

    @classmethod
    def test_provider(cls, provider_name: str, api_key: str, **kwargs: Any) -> Tuple[bool, str]:
        """
        Test de connexion pour n'importe quel provider.
        Détecte automatiquement le provider et utilise la bonne méthode.
        
        Args:
            provider_name: Nom du provider (ex: "OpenAI GPT-4o mini")
            api_key: Clé API du provider
            **kwargs: Arguments supplémentaires (ex: base_url)
            
        Returns:
            Tuple (succès: bool, message: str)
        """
        # Mapping des providers vers leurs méthodes de test
        provider_mapping = {
            "OpenAI GPT-4o mini": cls.test_openai,
            "Google Gemini 1.5 Flash": cls.test_google_gemini,
            "Google Gemini 2.5 Flash-Lite": cls.test_google_gemini,
            "Anthropic Claude Opus 4.5": cls.test_anthropic_claude,
            "Meta Llama 3 (via Groq)": cls.test_groq_llama,
            "Mistral NeMo": cls.test_mistral,
            "DeepSeek-V3": cls.test_deepseek,
            "DeepSeek-VL": cls.test_deepseek_vl,
            "Hugging Face (Mistral/Mixtral)": cls.test_huggingface,
            "IAKA (Interne)": lambda k: cls.test_iaka(k, kwargs.get('base_url', ''), kwargs.get('model', 'mistral-small'))
        }
        
        # Récupération de la méthode appropriée
        test_method = provider_mapping.get(provider_name)
        
        if test_method is None:
            return False, f"Provider '{provider_name}' non supporté. Providers disponibles: {', '.join(provider_mapping.keys())}"
        
        # Exécution du test
        return test_method(api_key)

    @classmethod
    def generate_response(cls, provider_name: str, api_key: str, messages: List[Dict[str, str]], **kwargs: Any) -> Tuple[bool, str]:
        """
        Generate a response using the specified provider.
        
        Args:
            provider_name: Name of the provider
            api_key: API Key
            messages: List of message dictionaries containing 'role' and 'content'
            **kwargs: Additional arguments like model, base_url, etc.
            
        Returns:
            Tuple (success: bool, content: str)
        """
        if "OpenAI" in provider_name:
            return cls.generate_openai(api_key, messages, **kwargs)
        elif "Gemini" in provider_name or "Google" in provider_name:
            return cls.generate_gemini(api_key, messages, **kwargs)
        elif "Claude" in provider_name or "Anthropic" in provider_name:
            return cls.generate_anthropic(api_key, messages, **kwargs)
        elif "Groq" in provider_name or "Llama" in provider_name:
            return cls.generate_groq(api_key, messages, **kwargs)
        elif "Hugging Face" in provider_name:
            # Handle Hugging Face (before Mistral to avoid ambiguity)
            return cls.generate_huggingface(api_key, messages, **kwargs)
        elif "Mistral" in provider_name:
            return cls.generate_mistral(api_key, messages, **kwargs)
        elif "DeepSeek" in provider_name:
            # DeepSeek is OpenAI compatible
            return cls.generate_openai_compatible(api_key, messages, base_url="https://api.deepseek.com", model="deepseek-chat", **kwargs)
        elif "IAKA" in provider_name:
            # Handle IAKA specifically
            base_url = kwargs.get('base_url')
            model_name = kwargs.get('model', 'mistral-small')
            
            if not base_url:
                return False, "Endpoint manquant pour IAKA"
                
            clean_base_url = base_url.rstrip('/')
            full_url = f"{clean_base_url}/{model_name}/v1"
            
            # base_url is already in kwargs, but we want to pass the modified full_url
            # and we don't want to pass base_url twice.
            kwargs.pop('base_url', None)

            return cls.generate_openai_compatible(api_key, messages, base_url=full_url, model=model_name, **kwargs)
        
        return False, f"Provider {provider_name} non supporté pour la génération."
