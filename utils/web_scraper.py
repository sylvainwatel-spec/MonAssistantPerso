from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import logging
import time

class WebScraper:
    def __init__(self):
        pass

    def fetch_page(self, url):
        """
        Récupère le contenu HTML d'une page URL via Playwright.
        Retourne un objet BeautifulSoup ou None en cas d'erreur.
        """
        try:
            with sync_playwright() as p:
                # Lancer le navigateur en mode headless (sans interface graphique)
                browser = p.chromium.launch(headless=True)
                
                # Créer un contexte avec un User-Agent réaliste
                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
                
                page = context.new_page()
                
                # Aller sur la page
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

    def perform_search(self, url, query):
        """
        Tente d'effectuer une recherche sur la page donnée.
        Cherche un champ input de type text/search, le remplit et valide.
        Retourne le texte de la page de résultats.
        """
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
                page = context.new_page()
                
                logging.info(f"Navigation vers {url} pour recherche '{query}'...")
                page.goto(url, timeout=30000)
                page.wait_for_load_state("networkidle")
                
                # Stratégie pour trouver la barre de recherche
                # 1. Chercher un input avec type="search"
                # 2. Chercher un input avec name="q" ou "query" ou "search"
                # 3. Chercher un input visible
                
                search_input = page.locator('input[type="search"]').first
                if not search_input.count():
                    search_input = page.locator('input[name="q"]').first
                if not search_input.count():
                    search_input = page.locator('input[name="query"]').first
                if not search_input.count():
                    search_input = page.locator('input[name="search"]').first
                
                # Si toujours rien, on prend le premier input text visible
                if not search_input.count():
                    # Filtrer pour avoir un input visible et editable
                    inputs = page.locator('input[type="text"]')
                    for i in range(inputs.count()):
                        if inputs.nth(i).is_visible():
                            search_input = inputs.nth(i)
                            break
                            
                if search_input and search_input.count():
                    search_input.fill(query)
                    search_input.press("Enter")
                    
                    # Attendre les résultats
                    page.wait_for_load_state("networkidle")
                    time.sleep(3) # Attente pour le rendu JS
                    
                    content = page.content()
                    browser.close()
                    
                    soup = BeautifulSoup(content, 'html.parser')
                    return self.extract_text(soup)
                else:
                    browser.close()
                    return "Impossible de trouver une barre de recherche sur cette page."
                    
        except Exception as e:
            logging.error(f"Erreur recherche: {e}")
            return f"Erreur lors de la recherche : {e}"
