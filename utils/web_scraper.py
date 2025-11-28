from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import logging
import time
import random
from utils.instruction_parser import InstructionParser

class WebScraper:
    def __init__(self):
        self.parser = InstructionParser()

    def fetch_page(self, url):
        """
        Récupère le contenu HTML d'une page URL via Playwright.
        Retourne un objet BeautifulSoup ou None en cas d'erreur.
        """
        try:
            with sync_playwright() as p:
                # Lancer le navigateur en mode visible pour permettre l'intervention humaine (CAPTCHA)
                # Masquer le flag d'automatisation pour éviter la détection
                browser = p.chromium.launch(
                    headless=False, 
                    slow_mo=1000,
                    args=['--disable-blink-features=AutomationControlled']
                )
                
                # Créer un contexte avec un User-Agent réaliste
                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
                
                page = context.new_page()
                
                # Aller sur la page avec un délai aléatoire
                time.sleep(random.uniform(1, 3))
                logging.info(f"Navigation vers {url}...")
                page.goto(url, timeout=30000)
                
                # Attendre un peu que le JS s'exécute
                page.wait_for_load_state("networkidle")
                time.sleep(2) # Petite pause supplémentaire de sécurité
                
                # Récupérer le contenu HTML
                content = page.content()
                
                browser.close()
                
                return BeautifulSoup(content, 'html.parser')
                
        except Exception as e:
            logging.error(f"Erreur lors de la récupération de {url} avec Playwright: {e}")
            return None

    def extract_text(self, soup, selector=None):
        """
        Extrait le texte d'une page ou d'un élément spécifique.
        Si selector est fourni, extrait le texte de cet élément.
        Sinon, extrait tout le texte de la page.
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

    def perform_search(self, url, query, instructions=None):
        """
        Effectue une recherche sur la page donnée.
        
        Args:
            url (str): URL du site
            query (str): Requête de recherche
            instructions (str, optional): Instructions textuelles pour guider la recherche
            
        Returns:
            str: Texte des résultats de recherche
        """
        # Parser les instructions si fournies
        parsed_instructions = {}
        if instructions:
            try:
                parsed_instructions = self.parser.parse(instructions)
                is_valid, errors = self.parser.validate(parsed_instructions)
                if not is_valid:
                    logging.warning(f"Instructions invalides: {errors}")
                    logging.info("Utilisation de la détection automatique par défaut")
                    parsed_instructions = {}
                else:
                    logging.info(f"Instructions parsées avec succès: {parsed_instructions}")
            except Exception as e:
                logging.error(f"Erreur lors du parsing des instructions: {e}")
                logging.info("Utilisation de la détection automatique par défaut")
                parsed_instructions = {}
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=False, 
                    slow_mo=1000,
                    args=['--disable-blink-features=AutomationControlled']
                )
                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
                page = context.new_page()
                
                logging.info(f"Navigation vers {url} pour recherche '{query}'...")
                time.sleep(random.uniform(1, 3))
                page.goto(url, timeout=30000)
                page.wait_for_load_state("networkidle")
                
                # Exécuter les actions BEFORE_SEARCH si présentes
                if 'before_search' in parsed_instructions:
                    logging.info("Exécution des actions BEFORE_SEARCH...")
                    for action in parsed_instructions['before_search']:
                        self._execute_action(page, action)
                
                # Trouver le champ de recherche
                search_input = None
                if 'search_input' in parsed_instructions:
                    # Utiliser le sélecteur fourni
                    logging.info(f"Utilisation du sélecteur personnalisé: {parsed_instructions['search_input']}")
                    try:
                        search_input = page.locator(parsed_instructions['search_input']).first
                        if search_input.count() and search_input.is_visible():
                            logging.info("Champ de recherche trouvé avec le sélecteur personnalisé")
                        else:
                            logging.warning("Sélecteur personnalisé ne trouve pas d'élément visible")
                            search_input = None
                    except Exception as e:
                        logging.error(f"Erreur avec le sélecteur personnalisé: {e}")
                        search_input = None
                
                # Si pas de sélecteur personnalisé ou échec, utiliser la détection automatique
                if not search_input:
                    logging.info("Détection automatique du champ de recherche...")
                    search_input = self._find_search_input(page)
                
                if not search_input or not search_input.count():
                    browser.close()
                    return "Impossible de trouver une barre de recherche sur cette page."
                
                # Remplir le champ de recherche
                logging.info(f"Remplissage du champ avec: {query}")
                search_input.fill(query)
                
                # Soumettre la recherche
                if 'search_button' in parsed_instructions:
                    # Utiliser le bouton spécifié
                    logging.info(f"Clic sur le bouton: {parsed_instructions['search_button']}")
                    try:
                        button = page.locator(parsed_instructions['search_button']).first
                        if button.count() and button.is_visible():
                            button.click()
                        else:
                            logging.warning("Bouton non trouvé, utilisation de Enter")
                            search_input.press("Enter")
                    except Exception as e:
                        logging.error(f"Erreur avec le bouton: {e}, utilisation de Enter")
                        search_input.press("Enter")
                else:
                    # Appuyer sur Enter par défaut
                    search_input.press("Enter")
                
                # Attendre les résultats
                if 'wait_for' in parsed_instructions:
                    logging.info(f"Attente du sélecteur: {parsed_instructions['wait_for']}")
                    try:
                        page.wait_for_selector(parsed_instructions['wait_for'], timeout=10000)
                    except Exception as e:
                        logging.warning(f"Timeout en attendant {parsed_instructions['wait_for']}: {e}")
                else:
                    page.wait_for_load_state("networkidle")
                    time.sleep(3)
                
                # Extraire les résultats
                content = page.content()
                browser.close()
                
                soup = BeautifulSoup(content, 'html.parser')
                
                # Extraction structurée si spécifiée
                if 'extract' in parsed_instructions and parsed_instructions['extract']:
                    return self._extract_structured_results(soup, parsed_instructions)
                elif 'results' in parsed_instructions:
                    # Extraire uniquement la zone de résultats
                    return self.extract_text(soup, parsed_instructions['results'])
                else:
                    # Extraction par défaut
                    return self.extract_text(soup)
                    
        except Exception as e:
            logging.error(f"Erreur recherche: {e}")
            return f"Erreur lors de la recherche : {e}"
    
    def _find_search_input(self, page):
        """
        Détection automatique du champ de recherche.
        Essaie plusieurs sélecteurs communs.
        """
        start_time = time.time()
        search_input = None
        
        logging.info("Attente de la barre de recherche... (Si un CAPTCHA apparait, merci de le résoudre)")
        
        while time.time() - start_time < 60:
            # 1. Chercher un input avec type="search"
            search_input = page.locator('input[type="search"]').first
            if not search_input.count() or not search_input.is_visible():
                search_input = page.locator('input[name="q"]').first
            if not search_input.count() or not search_input.is_visible():
                search_input = page.locator('input[name="query"]').first
            if not search_input.count() or not search_input.is_visible():
                search_input = page.locator('input[name="search"]').first
            
            # Si toujours rien, on prend le premier input text visible
            if not search_input.count() or not search_input.is_visible():
                inputs = page.locator('input[type="text"]')
                for i in range(inputs.count()):
                    if inputs.nth(i).is_visible():
                        search_input = inputs.nth(i)
                        break
            
            if search_input and search_input.count() and search_input.is_visible():
                logging.info("Barre de recherche trouvée !")
                return search_input
                
            time.sleep(2)
        
        return search_input
    
    def _execute_action(self, page, action):
        """
        Exécute une action Playwright selon le type.
        
        Args:
            page: Page Playwright
            action (dict): Action à exécuter avec 'type' et paramètres
        """
        action_type = action.get('type')
        
        try:
            if action_type == 'click':
                selector = action.get('selector')
                logging.info(f"Action CLICK: {selector}")
                element = page.locator(selector).first
                if element.count() and element.is_visible():
                    element.click()
                    time.sleep(1)  # Petite pause après le clic
                else:
                    logging.warning(f"Élément non trouvé ou invisible: {selector}")
                    
            elif action_type == 'wait':
                duration = action.get('duration', 1000)
                logging.info(f"Action WAIT: {duration}ms")
                time.sleep(duration / 1000.0)
                
            elif action_type == 'type':
                selector = action.get('selector')
                text = action.get('text')
                logging.info(f"Action TYPE: {selector} -> {text}")
                element = page.locator(selector).first
                if element.count() and element.is_visible():
                    element.fill(text)
                else:
                    logging.warning(f"Élément non trouvé ou invisible: {selector}")
            else:
                logging.warning(f"Type d'action inconnu: {action_type}")
                
        except Exception as e:
            logging.error(f"Erreur lors de l'exécution de l'action {action_type}: {e}")
    
    def _extract_structured_results(self, soup, parsed_instructions):
        """
        Extrait les résultats de manière structurée selon les champs spécifiés.
        
        Args:
            soup: BeautifulSoup object
            parsed_instructions (dict): Instructions parsées avec 'extract' et optionnellement 'results'
            
        Returns:
            str: Résultats formatés
        """
        extract_fields = parsed_instructions.get('extract', {})
        results_selector = parsed_instructions.get('results')
        
        if not extract_fields:
            return self.extract_text(soup)
        
        results = []
        
        # Si un sélecteur de résultats est spécifié, itérer sur chaque résultat
        if results_selector:
            result_elements = soup.select(results_selector)
            logging.info(f"Trouvé {len(result_elements)} résultats avec le sélecteur {results_selector}")
            
            for i, result_elem in enumerate(result_elements):
                result_data = {}
                for field_name, field_selector in extract_fields.items():
                    # Chercher le champ dans le contexte du résultat
                    field_elem = result_elem.select_one(field_selector)
                    if field_elem:
                        result_data[field_name] = field_elem.get_text(strip=True)
                    else:
                        result_data[field_name] = "N/A"
                
                # Formater le résultat
                result_str = f"Résultat {i+1}:\n"
                for field_name, value in result_data.items():
                    result_str += f"  {field_name}: {value}\n"
                results.append(result_str)
        else:
            # Pas de sélecteur de résultats, extraire les champs globalement
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
