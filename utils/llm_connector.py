"""
Module de connexion aux différents LLM providers.
Chaque provider a sa propre méthode de test de connexion.
"""

from typing import Tuple


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
            
            return True, f"Connexion réussie à OpenAI !\nModèle: gpt-3.5-turbo\nRéponse: {response.choices[0].message.content}"
            
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
            
            # Lister les modèles disponibles
            available_models = []
            try:
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        # Filtrer les modèles expérimentaux/preview qui ont des quotas limités
                        model_name = m.name.lower()
                        if 'preview' not in model_name and 'exp' not in model_name and 'experimental' not in model_name:
                            available_models.append(m.name)
            except Exception as e:
                return False, f"Erreur lors de la récupération des modèles Gemini.\n\nVérifiez votre clé API sur https://aistudio.google.com/app/apikey\n\nDétails: {str(e)}"
            
            if not available_models:
                return False, "Aucun modèle Gemini stable disponible avec cette clé API.\n\nLes modèles expérimentaux ont été exclus car ils ont des quotas très limités.\n\nVérifiez que votre clé API est valide et active."
            
            # Prioriser les modèles flash (plus rapides et quotas généreux)
            flash_models = [m for m in available_models if 'flash' in m.lower()]
            if flash_models:
                model_full_name = flash_models[0]
            else:
                model_full_name = available_models[0]
            
            try:
                # Créer le modèle en utilisant le nom complet
                model = genai.GenerativeModel(model_full_name)
                
                # Test avec une requête simple
                response = model.generate_content("Hello")
                
                # Extraire la réponse
                response_text = response.text if hasattr(response, 'text') else str(response)
                
                # Extraire juste le nom du modèle (sans "models/")
                model_name = model_full_name.replace('models/', '')
                
                return True, f"Connexion réussie à Google Gemini !\nModèle: {model_name}\nModèles stables disponibles: {len(available_models)}\nRéponse: {response_text[:50]}..."
                
            except Exception as e:
                error_msg = str(e)
                
                # Si c'est une erreur de quota, essayer le modèle suivant
                if '429' in error_msg or 'quota' in error_msg.lower():
                    # Essayer les autres modèles disponibles
                    for alt_model in available_models[1:]:
                        try:
                            model = genai.GenerativeModel(alt_model)
                            response = model.generate_content("Hello")
                            response_text = response.text if hasattr(response, 'text') else str(response)
                            model_name = alt_model.replace('models/', '')
                            return True, f"Connexion réussie à Google Gemini !\nModèle: {model_name} (fallback)\nRéponse: {response_text[:50]}..."
                        except:
                            continue
                    
                    return False, f"Quota dépassé pour tous les modèles Gemini disponibles.\n\nAttendez quelques minutes ou utilisez un autre provider.\n\nConsultez vos quotas: https://ai.dev/usage?tab=rate-limit"
                
                return False, f"Erreur lors du test avec le modèle {model_full_name}:\n\n{error_msg}"
            
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
            
            return True, f"Connexion réussie à Anthropic Claude !\nModèle: claude-3-haiku\nRéponse: {response.content[0].text}"
            
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
                temperature=0,
            )
            
            return True, f"Connexion réussie à Groq (Llama 3) !\nModèle: llama-3.1-8b-instant\nRéponse: {response.choices[0].message.content}"
            
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
            
            return True, f"Connexion réussie à Mistral AI !\nModèle: mistral-small\nRéponse: {response.choices[0].message.content}"
            
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
                temperature=0,
            )
            
            return True, f"Connexion réussie à DeepSeek !\nModèle: deepseek-chat\nRéponse: {response.choices[0].message.content}"
            
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
                content = response.choices[0].message.content
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
                        content = response.choices[0].message.content
                    else:
                        raise e
                except:
                    raise e
            
            return True, f"Connexion réussie au provider compatible OpenAI !\nEndpoint: {base_url}\nModèle: {model_used}\nRéponse: {content}"
            
        except Exception as e:
            return False, f"Erreur Provider Compatible: {str(e)}"

    @classmethod
    def test_provider(cls, provider_name: str, api_key: str, **kwargs) -> Tuple[bool, str]:
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
