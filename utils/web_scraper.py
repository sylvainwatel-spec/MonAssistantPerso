from typing import Optional, Dict, Any, List, Union
from bs4 import BeautifulSoup
import logging
import time
import random
from utils.instruction_parser import InstructionParser

class WebScraper:
    """
    Scraper web utilisant Playwright pour interagir avec les pages dynamiques.
    Gère la récupération de contenu et l'exécution de recherches avec instructions.
    """
    
    def __init__(self) -> None:
        self.parser = InstructionParser()
        self.logger = logging.getLogger(__name__)

    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """
        Récupère le contenu HTML d'une page URL via Playwright.
        
        Args:
            url: L'URL à visiter.
            
        Returns:
            BeautifulSoup object du contenu ou None en cas d'erreur.
        """
        # Lazy import playwright only when needed
        from playwright.sync_api import sync_playwright
        
        playwright = None
        browser = None
        
        try:
            playwright = sync_playwright().start()
            # Lancer le navigateur en mode visible pour permettre l'intervention humaine (CAPTCHA)
            browser = playwright.chromium.launch(
                headless=False, 
                slow_mo=1000,
                args=['--disable-blink-features=AutomationControlled']
            )
            
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            page = context.new_page()
            
            # Aller sur la page avec un délai aléatoire
            time.sleep(random.uniform(1, 3))
            self.logger.info(f"Navigation vers {url}...")
            page.goto(url, timeout=60000) # Augmentation du timeout
            
            # Attendre un peu que le JS s'exécute
            try:
                page.wait_for_load_state("networkidle", timeout=10000)
            except Exception:
                self.logger.warning("Timeout waiting for networkidle, continuing anyway.")
                
            time.sleep(2) # Petite pause supplémentaire de sécurité
            
            content = page.content()
            return BeautifulSoup(content, 'html.parser')
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération de {url} avec Playwright: {e}")
            return None
        finally:
            if browser:
                browser.close()
            if playwright:
                playwright.stop()

    def extract_text(self, soup: BeautifulSoup, selector: Optional[str] = None) -> str:
        """
        Extrait le texte d'une page ou d'un élément spécifique.
        
        Args:
            soup: L'objet BeautifulSoup.
            selector: Sélecteur CSS optionnel.
            
        Returns:
            Le texte extrait.
        """
        if not soup:
            return ""
        
        if selector:
            elements = soup.select(selector)
            return "\n".join([elem.get_text(strip=True) for elem in elements])
        else:
            # Par défaut, on essaie de nettoyer un peu en prenant le body
            body = soup.find('body')
            if body:
                return body.get_text(separator='\n', strip=True)
            return soup.get_text(separator='\n', strip=True)

    def perform_search(self, url: str, query: str, instructions: Optional[str] = None) -> str:
        """
        Effectue une recherche sur la page donnée.
        
        Args:
            url: URL du site.
            query: Requête de recherche.
            instructions: Instructions textuelles pour guider la recherche.
            
        Returns:
            Texte des résultats de recherche ou message d'erreur.
        """
        # Parser les instructions si fournies
        parsed_instructions: Dict[str, Any] = {}
        if instructions:
            try:
                parsed_instructions = self.parser.parse(instructions)
                is_valid, errors = self.parser.validate(parsed_instructions)
                if not is_valid:
                    self.logger.warning(f"Instructions invalides: {errors}")
                    self.logger.info("Utilisation de la détection automatique par défaut")
                    parsed_instructions = {}
                else:
                    self.logger.info(f"Instructions parsées avec succès: {parsed_instructions}")
            except Exception as e:
                self.logger.error(f"Erreur lors du parsing des instructions: {e}")
                parsed_instructions = {}
        
        # Lazy import playwright only when needed
        from playwright.sync_api import sync_playwright, Browser, Playwright
        
        playwright: Optional[Playwright] = None
        browser: Optional[Browser] = None
        
        try:
            playwright = sync_playwright().start()
            browser = playwright.chromium.launch(
                headless=False, 
                slow_mo=1000,
                args=['--disable-blink-features=AutomationControlled']
            )
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            page = context.new_page()
            
            self.logger.info(f"Navigation vers {url} pour recherche '{query}'...")
            time.sleep(random.uniform(1, 3))
            page.goto(url, timeout=60000)
            
            try:
                page.wait_for_load_state("networkidle", timeout=10000)
            except Exception:
                pass
            
            # Exécuter les actions BEFORE_SEARCH si présentes
            if 'before_search' in parsed_instructions:
                self.logger.info("Exécution des actions BEFORE_SEARCH...")
                for action in parsed_instructions['before_search']:
                    self._execute_action(page, action)
            
            # Trouver le champ de recherche
            search_input = None
            if 'search_input' in parsed_instructions:
                self.logger.info(f"Utilisation du sélecteur: {parsed_instructions['search_input']}")
                try:
                    search_input = page.locator(parsed_instructions['search_input']).first
                    if not search_input.count() or not search_input.is_visible():
                        self.logger.warning("Sélecteur ne trouve pas d'élément visible")
                        search_input = None
                except Exception as e:
                    self.logger.error(f"Erreur avec le sélecteur: {e}")
                    search_input = None
            
            # Fallback ou obligatoire ?
            if not search_input and 'search_input' in parsed_instructions:
                 # Si on avait une instruction explicite mais qu'elle échoue, on peut tenter l'auto ou échouer.
                 # Le code original échouait si pas de sélecteur. On va garder ce comportement si instructions présentes.
                 return f"❌ Impossible de trouver le champ de recherche avec le sélecteur: {parsed_instructions.get('search_input')}"

            if not search_input:
                 # Si pas d'instructions, on tente l'auto-détection (non implémentée dans le code original pour perform_search sans instructions, 
                 # mais _find_search_input existait. On l'utilise ici si pas d'instructions.)
                 search_input = self._find_search_input(page)

            if not search_input:
                return "❌ Impossible de trouver le champ de recherche automatiquement. Veuillez configurer les instructions URL."

            # Remplir le champ de recherche
            self.logger.info(f"Remplissage du champ avec: {query}")
            search_input.fill(query)
            
            # Soumettre la recherche
            if 'search_button' in parsed_instructions:
                self.logger.info(f"Clic sur le bouton: {parsed_instructions['search_button']}")
                try:
                    button = page.locator(parsed_instructions['search_button']).first
                    if button.count() and button.is_visible():
                        button.click()
                    else:
                        self.logger.warning("Bouton non trouvé, utilisation de Enter")
                        search_input.press("Enter")
                except Exception as e:
                    self.logger.error(f"Erreur avec le bouton: {e}, utilisation de Enter")
                    search_input.press("Enter")
            else:
                search_input.press("Enter")
            
            # Attendre les résultats
            if 'wait_for' in parsed_instructions:
                self.logger.info(f"Attente du sélecteur: {parsed_instructions['wait_for']}")
                try:
                    page.wait_for_selector(parsed_instructions['wait_for'], timeout=10000)
                except Exception as e:
                    self.logger.warning(f"Timeout en attendant {parsed_instructions['wait_for']}: {e}")
            else:
                try:
                    page.wait_for_load_state("networkidle", timeout=5000)
                except:
                    time.sleep(3)
            
            # Extraire les résultats
            content = page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            if 'extract' in parsed_instructions and parsed_instructions['extract']:
                return self._extract_structured_results(soup, parsed_instructions)
            elif 'results' in parsed_instructions:
                return self.extract_text(soup, parsed_instructions['results'])
            else:
                return self.extract_text(soup)
                    
        except Exception as e:
            self.logger.error(f"Erreur recherche: {e}")
            return f"Erreur lors de la recherche : {e}"
        finally:
            if browser:
                browser.close()
            if playwright:
                playwright.stop()
    
    def _find_search_input(self, page: Any) -> Any:
        """
        Détection automatique du champ de recherche.
        """
        start_time = time.time()
        search_input = None
        
        self.logger.info("Attente de la barre de recherche... (Si un CAPTCHA apparait, merci de le résoudre)")
        
        # On essaie pendant 10 secondes max pour l'auto-détection
        while time.time() - start_time < 10:
            # 1. Chercher un input avec type="search"
            search_input = page.locator('input[type="search"]').first
            if search_input.count() and search_input.is_visible():
                break
                
            search_input = page.locator('input[name="q"]').first
            if search_input.count() and search_input.is_visible():
                break
                
            search_input = page.locator('input[name="query"]').first
            if search_input.count() and search_input.is_visible():
                break
                
            search_input = page.locator('input[name="search"]').first
            if search_input.count() and search_input.is_visible():
                break
            
            # Reset si pas trouvé
            search_input = None
            time.sleep(1)
        
        if search_input:
            self.logger.info("Barre de recherche trouvée !")
            return search_input
            
        return None
    
    def _execute_action(self, page: Any, action: Dict[str, Any]) -> None:
        """Exécute une action Playwright."""
        action_type = action.get('type')
        
        try:
            if action_type == 'click':
                selector = action.get('selector')
                if selector:
                    self.logger.info(f"Action CLICK: {selector}")
                    element = page.locator(selector).first
                    if element.count() and element.is_visible():
                        element.click()
                        time.sleep(1)
                    else:
                        self.logger.warning(f"Élément non trouvé ou invisible: {selector}")
                    
            elif action_type == 'wait':
                duration = action.get('duration', 1000)
                self.logger.info(f"Action WAIT: {duration}ms")
                time.sleep(duration / 1000.0)
                
            elif action_type == 'type':
                selector = action.get('selector')
                text = action.get('text')
                if selector and text:
                    self.logger.info(f"Action TYPE: {selector} -> {text}")
                    element = page.locator(selector).first
                    if element.count() and element.is_visible():
                        element.fill(text)
                    else:
                        self.logger.warning(f"Élément non trouvé ou invisible: {selector}")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'exécution de l'action {action_type}: {e}")
    
    def _extract_structured_results(self, soup: BeautifulSoup, parsed_instructions: Dict[str, Any]) -> str:
        """Extrait les résultats de manière structurée."""
        extract_fields = parsed_instructions.get('extract', {})
        results_selector = parsed_instructions.get('results')
        
        if not extract_fields:
            return self.extract_text(soup)
        
        results = []
        
        if results_selector:
            result_elements = soup.select(results_selector)
            self.logger.info(f"Trouvé {len(result_elements)} résultats avec le sélecteur {results_selector}")
            
            for i, result_elem in enumerate(result_elements):
                result_data = {}
                for field_name, field_selector in extract_fields.items():
                    field_elem = result_elem.select_one(field_selector)
                    result_data[field_name] = field_elem.get_text(strip=True) if field_elem else "N/A"
                
                result_str = f"Résultat {i+1}:\n"
                for field_name, value in result_data.items():
                    result_str += f"  {field_name}: {value}\n"
                results.append(result_str)
        else:
            result_data = {}
            for field_name, field_selector in extract_fields.items():
                elements = soup.select(field_selector)
                if elements:
                    result_data[field_name] = "\n".join([elem.get_text(strip=True) for elem in elements])
                else:
                    result_data[field_name] = "N/A"
            
            result_str = "Résultats extraits:\n"
            for field_name, value in result_data.items():
                result_str += f"{field_name}:\n{value}\n\n"
            results.append(result_str)
        
        return "\n".join(results) if results else "Aucun résultat trouvé."
