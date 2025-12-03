"""
AI-powered web scraper using ScrapeGraphAI.
Simplifie le scraping en utilisant des prompts en langage naturel au lieu de sélecteurs CSS.
"""

import logging
import traceback
from typing import Any, Dict, Optional, Union, Tuple
from utils.results_manager import ResultsManager

# Patch for ScrapeGraphAI compatibility
try:
    import utils.patch_langchain
except ImportError:
    pass

from scrapegraphai.graphs import SmartScraperGraph


class AIScraper:
    """
    Scraper intelligent utilisant l'IA pour extraire des données de sites web.
    Pas besoin de sélecteurs CSS - décrivez simplement ce que vous voulez en français.
    """
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini", provider: str = "openai", assistant_id: str = None, assistant_name: str = None) -> None:
        """
        Initialise le scraper IA.
        
        Args:
            api_key: Clé API pour le LLM
            model: Modèle à utiliser (gpt-4o-mini, gemini-pro, etc.)
            provider: Fournisseur LLM (openai, google, groq, etc.)
            assistant_id: ID de l'assistant (pour sauvegarder les résultats)
            assistant_name: Nom de l'assistant (pour sauvegarder les résultats)
        """
        self.api_key = api_key
        self.model = model
        self.provider = provider
        self.assistant_id = assistant_id
        self.assistant_name = assistant_name
        self.logger = logging.getLogger(__name__)
        self.results_manager = ResultsManager()
    
    def search(self, url: str, query: str, extraction_prompt: str) -> Tuple[Union[str, Dict[str, Any]], Optional[str]]:
        """
        Effectue une recherche intelligente sur un site web.
        
        Args:
            url: URL du site (ex: https://www.leboncoin.fr)
            query: Requête de recherche (ex: "vélos électriques Paris")
            extraction_prompt: Description de ce qu'on veut extraire
        
        Returns:
            Tuple (résultats formatés, chemin du fichier de sauvegarde)
        """
        try:
            # Construire l'URL de recherche
            if "?" in url:
                search_url = f"{url}&q={query}"
            else:
                search_url = f"{url}/recherche?text={query}"
            
            self.logger.info(f"Scraping URL: {search_url}")
            self.logger.info(f"Extraction prompt: {extraction_prompt}")
            
            # Configuration du scraper
            graph_config = {
                "llm": {
                    "api_key": self.api_key,
                    "model": self.model,
                },
                "verbose": True,
                "headless": False,  # Navigateur visible pour debugging
            }
            
            # Adaptation pour les providers spécifiques
            if "google" in self.provider.lower() or "gemini" in self.provider.lower():
                graph_config["llm"]["model"] = f"gemini/{self.model}"
            elif "groq" in self.provider.lower():
                graph_config["llm"]["model"] = f"groq/{self.model}"
            elif "openai" in self.provider.lower():
                graph_config["llm"]["model"] = f"openai/{self.model}"
            # Par défaut, on laisse tel quel (souvent interprété comme OpenAI)
            
            # Créer le scraper intelligent
            scraper = SmartScraperGraph(
                prompt=extraction_prompt,
                source=search_url,
                config=graph_config
            )
            
            # Exécuter le scraping
            self.logger.info("Démarrage du scraping avec IA...")
            result = scraper.run()
            
            self.logger.info(f"Scraping terminé. Résultat: {result}")
            
            # Formater le résultat pour l'affichage
            if isinstance(result, dict):
                formatted_result = self._format_result(result)
            else:
                formatted_result = str(result)
            
            # Sauvegarder les résultats
            filepath = self._save_scraping_result(
                url=search_url,
                query=query,
                extraction_prompt=extraction_prompt,
                raw_results=result,
                formatted_results=formatted_result
            )
            
            return formatted_result, filepath
                
        except Exception as e:
            error_str = str(e)
            self.logger.error(f"Erreur lors du scraping IA: {e}")
            traceback.print_exc()
            
            # Détection spécifique des erreurs de limite de tokens (413)
            if "413" in error_str or "rate_limit_exceeded" in error_str.lower() or "request too large" in error_str.lower():
                return (
                    "❌ **Requête trop volumineuse**\n\n"
                    "Le contenu de la page dépasse la limite de tokens du modèle.\n\n"
                    "**Solutions** :\n"
                    "1. Utilisez un modèle avec une limite plus élevée (ex: GPT-4o mini)\n"
                    "2. Réduisez la taille de votre prompt d'extraction\n"
                    "3. Ciblez une URL plus spécifique avec moins de contenu\n\n"
                    f"Détails : {error_str}"
                )
            
            # Détection spécifique des erreurs de quota
            elif "quota" in error_str.lower() or "429" in error_str:
                return (
                    "❌ **Quota API dépassé**\n\n"
                    "Votre clé OpenAI a atteint sa limite de quota.\n\n"
                    "**Solutions** :\n"
                    "1. Ajoutez des crédits sur votre compte OpenAI : https://platform.openai.com/account/billing\n"
                    "2. Ou changez de provider LLM (Gemini, Groq, etc.) dans la page Administration\n\n"
                    f"Détails : {error_str}"
                )
            
            # Détection des erreurs d'authentification
            elif "401" in error_str or "invalid" in error_str.lower() and "key" in error_str.lower():
                return (
                    "❌ **Clé API invalide**\n\n"
                    "Votre clé API n'est pas reconnue ou a expiré.\n\n"
                    "Veuillez vérifier votre clé dans la page Administration.\n\n"
                    f"Détails : {error_str}"
                )
            
            # Erreur générique
            error_message = (
                f"❌ **Erreur lors du scraping** : {error_str}\n\n"
                "**Vérifiez que** :\n"
                "- L'URL est accessible et correcte\n"
                "- Le prompt d'extraction est clair et précis\n"
                "- Votre clé API est valide et a du crédit disponible"
            )
            return error_message, None
    
    def _format_result(self, result: Union[Dict[str, Any], str]) -> str:
        """
        Formate le résultat JSON en texte lisible.
        
        Args:
            result: Résultat du scraping
            
        Returns:
            Résultat formaté
        """
        if not result:
            return "Aucun résultat trouvé."
        
        # Si le résultat contient une liste d'items
        if isinstance(result, dict) and any(isinstance(v, list) for v in result.values()):
            formatted = "📊 Résultats extraits:\n\n"
            
            for key, value in result.items():
                if isinstance(value, list):
                    formatted += f"**{key.upper()}**:\n"
                    for i, item in enumerate(value, 1):
                        if isinstance(item, dict):
                            formatted += f"\n  {i}. "
                            for field, field_value in item.items():
                                formatted += f"{field}: {field_value} | "
                            formatted = formatted.rstrip(" | ") + "\n"
                        else:
                            formatted += f"  {i}. {item}\n"
                    formatted += "\n"
                else:
                    formatted += f"**{key}**: {value}\n"
            
            return formatted.strip()
        
        # Si le résultat est un simple dictionnaire
        elif isinstance(result, dict):
            formatted = "📊 Résultat extrait:\n\n"
            for key, value in result.items():
                formatted += f"**{key}**: {value}\n"
            return formatted.strip()
        
        # Sinon, retourner tel quel
        return str(result)
    
    def _save_scraping_result(self, url: str, query: str, extraction_prompt: str, 
                              raw_results: Any, formatted_results: str) -> Optional[str]:
        """
        Sauvegarde les résultats de scraping dans un fichier JSON.
        
        Args:
            url: URL scrapée
            query: Requête de recherche
            extraction_prompt: Prompt d'extraction utilisé
            raw_results: Résultats bruts du scraper
            formatted_results: Résultats formatés pour affichage
        
        Returns:
            Chemin du fichier créé, ou None si erreur
        """
        try:
            data = {
                "assistant_id": self.assistant_id or "unknown",
                "assistant_name": self.assistant_name or "Unknown Assistant",
                "url": url,
                "query": query,
                "extraction_prompt": extraction_prompt,
                "results": formatted_results,
                "raw_results": raw_results,
                "provider": self.provider,
                "model": self.model
            }
            
            filepath = self.results_manager.save_result(data)
            self.logger.info(f"Résultats sauvegardés dans: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde des résultats: {e}")
            return None
    
    def simple_scrape(self, url: str, extraction_prompt: str) -> Tuple[Union[str, Dict[str, Any]], Optional[str]]:
        """
        Scrape simple d'une page sans recherche.
        
        Args:
            url: URL complète de la page
            extraction_prompt: Description de ce qu'on veut extraire
            
        Returns:
            Tuple (résultats formatés, chemin du fichier de sauvegarde)
        """
        try:
            self.logger.info(f"Scraping simple de: {url}")
            self.logger.info(f"Extraction prompt: {extraction_prompt}")
            
            # Configuration du scraper
            graph_config = {
                "llm": {
                    "api_key": self.api_key,
                    "model": self.model,
                },
                "verbose": True,
                "headless": False,
            }
            
            # Adaptation pour les providers spécifiques
            if "google" in self.provider.lower() or "gemini" in self.provider.lower():
                graph_config["llm"]["model"] = f"gemini/{self.model}"
            elif "groq" in self.provider.lower():
                graph_config["llm"]["model"] = f"groq/{self.model}"
            elif "openai" in self.provider.lower():
                graph_config["llm"]["model"] = f"openai/{self.model}"
            # Par défaut, on laisse tel quel
            
            scraper = SmartScraperGraph(
                prompt=extraction_prompt,
                source=url,
                config=graph_config
            )
            
            result = scraper.run()
            
            # Formater le résultat
            if isinstance(result, dict):
                formatted_result = self._format_result(result)
            else:
                formatted_result = str(result)
            
            # Sauvegarder les résultats
            filepath = self._save_scraping_result(
                url=url,
                query="",  # Pas de query pour simple_scrape
                extraction_prompt=extraction_prompt,
                raw_results=result,
                formatted_results=formatted_result
            )
            
            return formatted_result, filepath
                
        except Exception as e:
            error_str = str(e)
            self.logger.error(f"Erreur lors du scraping simple: {e}")
            traceback.print_exc()
            
            # Détection spécifique des erreurs de limite de tokens (413)
            if "413" in error_str or "rate_limit_exceeded" in error_str.lower() or "request too large" in error_str.lower():
                return (
                    "❌ **Requête trop volumineuse**\n\n"
                    "Le contenu de la page dépasse la limite de tokens du modèle.\n\n"
                    "**Solutions** :\n"
                    "1. Utilisez un modèle avec une limite plus élevée (ex: GPT-4o mini)\n"
                    "2. Réduisez la taille de votre prompt d'extraction\n"
                    "3. Ciblez une URL plus spécifique avec moins de contenu\n\n"
                    f"Détails : {error_str}"
                )
            
            # Détection spécifique des erreurs de quota
            elif "quota" in error_str.lower() or "429" in error_str:
                return (
                    "❌ **Quota API dépassé**\n\n"
                    "Votre clé OpenAI a atteint sa limite de quota.\n\n"
                    "**Solutions** :\n"
                    "1. Ajoutez des crédits sur votre compte OpenAI : https://platform.openai.com/account/billing\n"
                    "2. Ou changez de provider LLM (Gemini, Groq, etc.) dans la page Administration\n\n"
                    f"Détails : {error_str}"
                )
            
            # Détection des erreurs d'authentification
            elif "401" in error_str or "invalid" in error_str.lower() and "key" in error_str.lower():
                return (
                    "❌ **Clé API invalide**\n\n"
                    "Votre clé API n'est pas reconnue ou a expiré.\n\n"
                    "Veuillez vérifier votre clé dans la page Administration.\n\n"
                    f"Détails : {error_str}"
                )
            
            # Erreur générique
            error_message = (
                f"❌ **Erreur lors du scraping** : {error_str}\n\n"
                "**Vérifiez que** :\n"
                "- L'URL est accessible et correcte\n"
                "- Le prompt d'extraction est clair et précis\n"
                "- Votre clé API est valide et a du crédit disponible"
            )
            return error_message, None
