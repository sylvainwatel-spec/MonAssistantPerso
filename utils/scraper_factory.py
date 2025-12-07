"""
Factory Pattern pour créer les scrapers
Permet de choisir facilement entre ScrapeGraphAI et Playwright
"""

import logging
from typing import Any, Dict


class ScraperFactory:
    """
    Factory pour créer les scrapers selon le type choisi
    """
    
    @staticmethod
    def create_scraper(scraper_type: str, **kwargs) -> Any:
        """
        Crée le scraper approprié selon le type
        
        Args:
            scraper_type: "scrapegraphai" ou "playwright"
            **kwargs: Paramètres pour le scraper
                Pour ScrapeGraphAI:
                    - api_key: Clé API du LLM
                    - model: Modèle à utiliser
                    - provider: Provider LLM
                    - assistant_id: ID de l'assistant
                    - assistant_name: Nom de l'assistant
                Pour Playwright:
                    - assistant_id: ID de l'assistant
                    - assistant_name: Nom de l'assistant
        
        Returns:
            Instance de scraper (AIScraper ou PlaywrightScraper)
        
        Raises:
            ValueError: Si le type de scraper est inconnu
            ImportError: Si les dépendances ne sont pas installées
        """
        logger = logging.getLogger(__name__)
        
        if scraper_type == "scrapegraphai":
            try:
                from utils.ai_scraper import AIScraper
                logger.info("Création d'un scraper ScrapeGraphAI")
                # Filtrer les arguments non supportés par AIScraper
                sg_kwargs = {k: v for k, v in kwargs.items() if k != 'log_callback'}
                return AIScraper(**sg_kwargs)
            except ImportError as e:
                logger.error(f"Impossible d'importer AIScraper: {e}")
                raise ImportError(
                    "ScrapeGraphAI n'est pas installé. "
                    "Installez-le ou utilisez Playwright à la place."
                )
        
        elif scraper_type == "playwright":
            try:
                from utils.playwright_scraper import PlaywrightScraper
                logger.info("Création d'un scraper Playwright")
                # Filtrer les kwargs pour ne garder que ceux pertinents pour Playwright
                playwright_kwargs = {
                    'assistant_id': kwargs.get('assistant_id'),
                    'assistant_name': kwargs.get('assistant_name'),
                    'log_callback': kwargs.get('log_callback'),
                    'headless': kwargs.get('headless', True),
                    'browser_type': kwargs.get('browser_type', 'firefox'),
                    'llm_api_key': kwargs.get('llm_api_key'),
                    'llm_model': kwargs.get('llm_model')
                }
                return PlaywrightScraper(**playwright_kwargs)
            except ImportError as e:
                logger.error(f"Impossible d'importer PlaywrightScraper: {e}")
                raise ImportError(
                    "Playwright n'est pas installé. "
                    "Installez-le avec: pip install playwright && playwright install chromium"
                )
        
        else:
            raise ValueError(
                f"Type de scraper inconnu: {scraper_type}. "
                f"Utilisez 'scrapegraphai' ou 'playwright'."
            )
    
    @staticmethod
    def get_available_scrapers() -> Dict[str, bool]:
        """
        Vérifie quels scrapers sont disponibles
        
        Returns:
            Dictionnaire avec la disponibilité de chaque scraper
        """
        available = {}
        
        # Vérifier ScrapeGraphAI
        try:
            from utils.ai_scraper import AIScraper
            available['scrapegraphai'] = True
        except ImportError:
            available['scrapegraphai'] = False
        
        # Vérifier Playwright
        try:
            from utils.playwright_scraper import PlaywrightScraper
            from playwright.sync_api import sync_playwright
            available['playwright'] = True
        except ImportError:
            available['playwright'] = False
        
        return available
    
    @staticmethod
    def get_scraper_info(scraper_type: str) -> Dict[str, Any]:
        """
        Retourne les informations sur un type de scraper
        
        Args:
            scraper_type: "scrapegraphai" ou "playwright"
        
        Returns:
            Dictionnaire avec les informations du scraper
        """
        info = {
            "scrapegraphai": {
                "name": "ScrapeGraphAI",
                "description": "Scraping intelligent avec IA",
                "icon": "🤖",
                "cost": "~0.05€ par scraping",
                "speed": "Moyen (10-30s)",
                "requires_api_key": True,
                "advantages": [
                    "Utilise l'IA pour comprendre les pages",
                    "Prompts en langage naturel",
                    "S'adapte aux changements de structure"
                ],
                "disadvantages": [
                    "Coût par scraping",
                    "Dépend des quotas API",
                    "Peut avoir des erreurs 413/429"
                ]
            },
            "playwright": {
                "name": "Playwright",
                "description": "Scraping traditionnel gratuit",
                "icon": "🎭",
                "cost": "Gratuit",
                "speed": "Rapide (2-10s)",
                "requires_api_key": False,
                "advantages": [
                    "100% gratuit",
                    "Rapide et fiable",
                    "Pas de limite de tokens",
                    "Contrôle total"
                ],
                "disadvantages": [
                    "Nécessite des sélecteurs CSS",
                    "Peut nécessiter des ajustements si le site change",
                    "Installation de navigateur requise"
                ]
            }
        }
        
        return info.get(scraper_type, {})
