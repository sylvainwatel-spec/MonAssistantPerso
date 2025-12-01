"""
Module de connexion aux différents LLM providers.
Chaque provider a sa propre méthode de test de connexion.
"""

from typing import Tuple, Optional, Any, Dict

class LLMConnectionTester:
    """Classe pour tester les connexions aux différents LLM providers."""
    
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
            
            # Liste des modèles à tester (noms corrects pour API v1)
            models_to_test = [
                "models/gemini-1.5-flash",
                "models/gemini-1.5-flash-latest",
                "models/gemini-1.5-pro",
                "models/gemini-1.5-pro-latest",
                "gemini-1.5-flash",
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
                    
                    # Si c'est une erreur de quota, on arrête d'essayer
                    if '429' in error_msg or 'quota' in error_msg.lower() or 'resource_exhausted' in error_msg.lower():
                        return False, f"Quota dépassé pour Google Gemini.\n\nAttendez quelques minutes ou utilisez un autre provider.\n\nConsultez vos quotas: https://aistudio.google.com/apikey"
                    
                    # Si c'est une erreur d'authentification, on arrête
                    if '401' in error_msg or '403' in error_msg or 'invalid api key' in error_msg.lower():
                        return False, f"Clé API invalide ou non autorisée.\n\nVérifiez votre clé API sur https://aistudio.google.com/apikey\n\nDétails: {error_msg}"
                    
                    # Pour les erreurs 404, on continue avec le modèle suivant
                    if '404' in error_msg:
                        continue
                    
                    # Pour les autres erreurs, on continue aussi
                    continue
            
            # Si aucun modèle n'a fonctionné
            return False, f"Impossible de se connecter à Google Gemini.\n\nLa clé API semble valide mais aucun modèle n'est accessible.\n\nVérifiez que votre clé a les bonnes permissions sur:\nhttps://aistudio.google.com/apikey\n\nDernière erreur: {last_error[:200]}"
            
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
                model="claude-3-haiku-20240307",
                max_tokens=10,
                messages=[{"role": "user", "content": "Hello"}]
            )
            
            content = response.content[0].text if response.content else ""
            return True, f"Connexion réussie à Anthropic Claude !\nModèle: claude-3-haiku\nRéponse: {content}"
            
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
            from mistralai.client import MistralClient
            
            client = MistralClient(api_key=api_key)
            
            # Requête minimale pour vérifier la clé
            response = client.chat(
                model="mistral-small-latest",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5,
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
            "Anthropic Claude 3 Haiku": cls.test_anthropic_claude,
            "Meta Llama 3 (via Groq)": cls.test_groq_llama,
            "Mistral NeMo": cls.test_mistral,
            "DeepSeek-V3": cls.test_deepseek,
            "IAKA (Interne)": lambda k: cls.test_openai_compatible(k, kwargs.get('base_url', ''))
        }
        
        # Récupération de la méthode appropriée
        test_method = provider_mapping.get(provider_name)
        
        if test_method is None:
            return False, f"Provider '{provider_name}' non supporté. Providers disponibles: {', '.join(provider_mapping.keys())}"
        
        # Exécution du test
        return test_method(api_key)
