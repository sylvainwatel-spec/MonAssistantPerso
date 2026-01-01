"""
Scraper basé sur Playwright - Alternative gratuite à ScrapeGraphAI
Compatible avec l'interface AIScraper pour faciliter l'intégration
"""

import logging
import random
import time
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from utils.results_manager import ResultsManager


class PlaywrightScraper:
    """
    Scraper web utilisant Playwright
    Alternative 100% gratuite à ScrapeGraphAI
    
    Avantages:
    - Gratuit (pas de coût API)
    - Rapide
    - Fiable
    - Contrôle total sur l'extraction
    """
    
    def __init__(self, assistant_id: str = None, assistant_name: str = None, log_callback: callable = None, headless: bool = True, browser_type: str = "chromium", llm_api_key: str = None, llm_model: str = None):
        """
        Initialise le scraper Playwright
        
        Args:
            assistant_id: ID de l'assistant (pour sauvegarde des résultats)
            assistant_name: Nom de l'assistant (pour sauvegarde des résultats)
            log_callback: Fonction de callback pour les logs (ex: affichage dans le chat)
            headless: Mode sans interface graphique (True) ou visible (False)
            browser_type: "chromium" (défaut), "firefox", "chrome" (système), "msedge" (système)
            llm_api_key: Clé API pour fonctionnalités Vision (optionnel)
            llm_model: Modèle pour Vision (optionnel)
        """
        self.assistant_id = assistant_id
        self.assistant_name = assistant_name
        self.log_callback = log_callback
        self.headless = headless
        self.browser_type = browser_type
        self.llm_api_key = llm_api_key
        self.llm_model = llm_model
        self.logger = logging.getLogger(__name__)
        self.results_manager = ResultsManager()
        self.playwright = None
        self.browser = None
        self.playwright = None
        self.browser = None
        self.context = None
        self.storage_state_path = "browser_context.json"  # Fichier contextuel global

    def _log(self, message: str):
        """Log un message via le logger et le callback si présent."""
        self.logger.info(message)
        if self.log_callback:
            try:
                self.log_callback(message)
            except Exception as e:
                self.logger.error(f"Erreur dans le callback de log: {e}")
    
    def __enter__(self):
        """Context manager - Démarrer le navigateur"""
        try:
            # Patch pour éviter l'erreur "Sync API inside asyncio loop"
            try:
                import nest_asyncio
                nest_asyncio.apply()
            except ImportError:
                pass

            from playwright.sync_api import sync_playwright
            # Ne pas importer stealth ici si on veut l'appliquer page par page, 
            # mais on peut vérifier l'import
            # Tester stealth ici (import seulement pour vérification)
            try:
                from playwright_stealth import Stealth
                self._has_stealth = True
            except ImportError as e:
                self._has_stealth = False
                self._log(f"⚠️ module 'playwright-stealth' manquant. Mode furtif désactivé. Erreur: {e}")
            
            # Désactiver stealth pour Firefox (instable/incompatible)
            if self.browser_type == "firefox":
                self._has_stealth = False
            
            self._log(f"Démarrage de Playwright ({self.browser_type}, Headless: {self.headless})...")
            self.playwright = sync_playwright().start()
            
            # Pause aléatoire avant lancement du navigateur (simulation humaine)
            launch_delay = random.uniform(1.0, 3.0)
            self._log(f"Pause pré-lancement ({launch_delay:.1f}s)...")
            time.sleep(launch_delay)
            
            # Préparation User-Agent et Viewport (déplacé avant launch pour persistent context)
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0", 
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:125.0) Gecko/20100101 Firefox/125.0",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0"
            ]
            ua = random.choice(user_agents)
            
            viewports = [
                {'width': 1920, 'height': 1080},
                {'width': 1366, 'height': 768},
                {'width': 1536, 'height': 864},
                {'width': 1440, 'height': 900},
            ]
            vp = random.choice(viewports)
            self._log(f"Config contexte: {vp['width']}x{vp['height']}")
            
            self.context = None # Sera rempli si persistent context
            
            if self.browser_type == "firefox":
                self._log(f"Lancement de Firefox...")
                
                import os
                
                executable_path = self._find_browser_executable("firefox")
                
                # Configuration Firefox (mode standard uniquement - persistent context bloque)
                launch_kwargs = {
                    "headless": self.headless,
                    "args": [
                        "-no-remote",  # Permet plusieurs instances Firefox
                        "-new-instance"  # Force nouvelle instance
                    ]
                }
                
                if executable_path:
                    self._log(f"🕸️ Utilisation de Firefox système : {executable_path}")
                    launch_kwargs["executable_path"] = executable_path
                
                # Lancement Firefox Standard (Persistent Context bloque avec Firefox système)
                try:
                    self._log(f"Lancement Firefox Standard (Persistent non supporté pour Firefox)...")
                    self.browser = self.playwright.firefox.launch(**launch_kwargs)
                    self.context = None  # Will be created later with storage_state
                    self._log("✅ Succès lancement Firefox Standard.")
                    
                except Exception as e:
                    error_msg = str(e)
                    if "Target page, context or browser has been closed" in error_msg:
                        self._log("⚠️ Firefox système a fermé la connexion (Protection ou conflit).")
                    else:
                        self._log(f"⚠️ Erreur lancement Firefox: {error_msg}")
                    
                    # Fallback Chromium Bundled
                    self._log("🔄 Fallback sur Chromium (Bundled)...")
                    self.browser = self.playwright.chromium.launch(
                        headless=self.headless,
                        args=['--no-sandbox', '--disable-infobars', '--start-maximized']
                    )
                    self.context = None
            elif self.browser_type in ["chrome", "msedge"]:
                self._log(f"Lancement du navigateur système : {self.browser_type}")
                
                import os
                
                # Tentative de détection manuelle du chemin
                executable_path = self._find_browser_executable(self.browser_type)
                
                # Configuration commune
                launch_kwargs = {
                    "headless": self.headless,
                    "viewport": vp,
                    "args": ["--start-maximized", "--no-sandbox", "--disable-infobars"]
                }
                
                if executable_path:
                    self._log(f"Exécutable trouvé : {executable_path}")
                    launch_kwargs["executable_path"] = executable_path
                else:
                    launch_kwargs["channel"] = self.browser_type
                    self._log(f"Exécutable non trouvé, utilisation du channel: {self.browser_type}")

                # 1. Tentative Persistent Context (Plus risqué mais garde les cookies)
                try:
                    self._log(f"Tentative 1: Mode Persistent...")
                    
                    # Dossier de profil dédié
                    base_dir = os.path.dirname(self.storage_state_path)
                    user_data_dir = os.path.join(base_dir, f"{self.browser_type}_persistent_profile")
                    if not os.path.exists(user_data_dir):
                        os.makedirs(user_data_dir, exist_ok=True)
                        
                    # Persistent needs user_data_dir as first arg
                    persistent_kwargs = launch_kwargs.copy()
                    
                    # Persistent launch can be finicky with args, keep it simple
                    if "args" in persistent_kwargs:
                        # Some args might conflict with persistent mode
                        persistent_kwargs["args"] = [a for a in persistent_kwargs["args"] if a != "--start-maximized"]

                    self.context = self.playwright.chromium.launch_persistent_context(
                        user_data_dir,
                        user_agent=ua,
                        locale='fr-FR',
                        timezone_id='Europe/Paris',
                        **persistent_kwargs
                    )
                    self.browser = None # Browser managed by context
                    self._log("✅ Succès lancement Persistent.")
                    
                except Exception as e:
                    self._log(f"⚠️ Échec lancement Persistent: {e}")
                    
                    # 2. Tentative Standard Launch (Système)
                    try:
                        self._log(f"Tentative 2: Mode Standard (Non-Persistent) sur {self.browser_type}...")
                        self.browser = self.playwright.chromium.launch(**launch_kwargs)
                        self.context = None # Will be created later
                        self._log("✅ Succès lancement Standard.")
                        
                    except Exception as e2:
                        self._log(f"⚠️ Échec lancement Standard: {e2}")
                        
                        # 3. Tentative Fallback Chromium Bundled
                        self._log("🔄 Tentative 3: Fallback sur Chromium (Bundled)...")
                        self.browser = self.playwright.chromium.launch(
                            headless=self.headless,
                            args=['--no-sandbox', '--disable-infobars', '--start-maximized']
                        )
                        self.context = None
            else:
                self.browser = self.playwright.chromium.launch(
                    headless=self.headless,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-infobars',
                        '--start-maximized'
                    ]
                )
            
            # Pause explicite post-lancement à vide demandée par l'utilisateur
            self._log("Navigateur prêt (vide). Pause de stabilisation (5s)...")
            time.sleep(5)

            # Création du contexte standard SI ce n'est pas un contexte persistent
            if not self.context:
                # Vérifier si un état sauvegardé existe (pour session standard)
                import os
                storage_params = {}
                if os.path.exists(self.storage_state_path):
                    self._log(f"Chargement de la session existante depuis {self.storage_state_path}")
                    storage_params = {"storage_state": self.storage_state_path}
                
                # Configuration du contexte avec User-Agent réaliste et Storage
                self.context = self.browser.new_context(
                    viewport=vp,
                    user_agent=ua,
                    locale='fr-FR',
                    timezone_id='Europe/Paris',
                    **storage_params
                )
            
            # Appliquer stealth au contexte entier (si disponible)
            if hasattr(self, '_has_stealth') and self._has_stealth and not self.browser_type == "firefox":
                try:
                    from playwright_stealth import Stealth
                    Stealth().apply_stealth_sync(self.context)
                    self._log("✅ Mode stealth activé sur le contexte.")
                except Exception as e:
                    self._log(f"⚠️ Erreur application stealth au contexte: {e}")
            
            self._log("Navigateur Playwright prêt.")
            return self
        except ImportError:
            msg = "Playwright n'est pas installé. Installez-le avec: pip install playwright && playwright install chromium"
            self.logger.error(msg)
            if self.log_callback: self.log_callback(f"❌ {msg}")
            raise
        except Exception as e:
            self.logger.error(f"Erreur lors du démarrage de Playwright: {e}")
            raise
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager - Fermer le navigateur"""
        try:
            if self.context:
                # Sauvegarder l'état (cookies, storage) pour la prochaine fois
                try:
                    self.context.storage_state(path=self.storage_state_path)
                    self._log(f"Session sauvegardée dans {self.storage_state_path}")
                except Exception as e:
                    self._log(f"Erreur sauvegarde session: {e}")
                
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            self._log("Fermeture de Playwright.")
        except Exception as e:
            self.logger.warning(f"Erreur lors de la fermeture de Playwright: {e}")
    
    def _simulate_human_behavior(self, page):
        """Simule des mouvements de souris et des scrolls pour tromper les protections."""
        try:
            self._log("🤖 Simulation d'activité humaine...")
            # Mouvements de souris aléatoires
            for _ in range(random.randint(2, 4)):
                 x = random.randint(100, 1000)
                 y = random.randint(100, 800)
                 page.mouse.move(x, y)
                 time.sleep(random.uniform(0.1, 0.4))
                 
            # Scroll avec pause
            page.mouse.wheel(0, random.randint(200, 600))
            time.sleep(random.uniform(0.5, 1.0))
            page.mouse.wheel(0, -random.randint(50, 200)) # Remonter un peu
            time.sleep(random.uniform(0.5, 1.0))
            
        except Exception as e:
            self._log(f"Erreur simulation humaine: {e}")
        except Exception as e:
            self._log(f"Erreur simulation humaine: {e}")

    def _find_browser_executable(self, browser_type: str) -> Optional[str]:
        """Tente de trouver le chemin de l'exécutable du navigateur système."""
        import os
        paths = []
        
        local_app_data = os.getenv('LOCALAPPDATA', '')
        program_files = os.getenv('ProgramFiles', '')
        program_files_x86 = os.getenv('ProgramFiles(x86)', '')
        
        if browser_type == "chrome":
            paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe", # User provided
                os.path.join(program_files, 'Google', 'Chrome', 'Application', 'chrome.exe'),
                os.path.join(program_files_x86, 'Google', 'Chrome', 'Application', 'chrome.exe'),
                os.path.join(local_app_data, 'Google', 'Chrome', 'Application', 'chrome.exe')
            ]
        elif browser_type == "msedge":
             paths = [
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", # User provided
                os.path.join(program_files, 'Microsoft', 'Edge', 'Application', 'msedge.exe'),
                os.path.join(program_files_x86, 'Microsoft', 'Edge', 'Application', 'msedge.exe'),
                os.path.join(local_app_data, 'Microsoft', 'Edge', 'Application', 'msedge.exe')
             ]
        elif browser_type == "firefox":
            paths = [
                r"C:\Program Files\Mozilla Firefox\firefox.exe", # User provided
                os.path.join(program_files, 'Mozilla Firefox', 'firefox.exe'),
                os.path.join(program_files_x86, 'Mozilla Firefox', 'firefox.exe'),
            ]
        
        for path in paths:
            if path and os.path.exists(path):
                return path
        return None

    def search(self, url: str, query: str, extraction_prompt: str = None) -> Tuple[str, Optional[str]]:
        """
        Effectue une recherche sur un site web
        Interface compatible avec AIScraper.search()
        
        Args:
            url: URL du site (ex: https://www.leboncoin.fr)
            query: Requête de recherche
            extraction_prompt: Description de ce qu'on veut extraire (optionnel, pour compatibilité)
        
        Returns:
            Tuple (résultats formatés, chemin du fichier de sauvegarde)
        """
        try:
            self._log(f"Début de la recherche sur {url} pour '{query}'")
            
            # Utiliser le context manager pour gérer le cycle de vie du navigateur
            with self:
                # Déterminer le type de site et utiliser le scraper approprié
                if "leboncoin.fr" in url.lower():
                    results = self._scrape_leboncoin(url, query)
                else:
                    results = self._scrape_generic(url, query)
            
            # Formater les résultats
            formatted = self._format_results(results)
            
            # Sauvegarder
            filepath = self._save_results(url, query, extraction_prompt or "", results, formatted)
            
            self._log(f"Scraping terminé. {len(results)} résultats trouvés.")
            return formatted, filepath
            
        except Exception as e:
            error_str = str(e)
            self.logger.error(f"Erreur lors du scraping: {error_str}")
            
            # Gestion spécifique fermeture navigateur
            if "Target page, context or browser has been closed" in error_str or "TargetClosedError" in error_str:
                error_message = (
                    "⚠️ **Scraping interrompu**\n"
                    "Le navigateur a été fermé (manuellement ou plantage).\n"
                    "Si vous avez fermé la fenêtre, c'est normal."
                )
                if self.log_callback: self.log_callback("⚠️ Navigateur fermé. Scraping annulé.")
                return error_message, None

            import traceback
            error_message = f"Erreur scraping inconnue: {error_str}"
            return error_message, None
    
    def _analyze_with_vision(self, image_bytes: bytes, prompt: str) -> List[Dict]:
        """Analyse une image avec Gemini Vision pour extraire des données."""
        if not self.llm_api_key:
            self._log("⚠️ Pas de clé API LLM pour la vision. Extraction impossible.")
            return []
        
        try:
            import google.generativeai as genai
            from PIL import Image
            import io
            import json

            self._log(f"🧠 Analyse Vision ({self.llm_model or 'gemini-1.5-flash'})...")
            
            genai.configure(api_key=self.llm_api_key)
            model = genai.GenerativeModel(self.llm_model or 'gemini-1.5-flash')
            
            image = Image.open(io.BytesIO(image_bytes))
            
            # Prompt explicite pour JSON
            full_prompt = f"""
            {prompt}
            
            Strictly return a valid JSON array of objects.
            Format: [ {{"title": "...", "price": "...", "location": "...", "url": "..."}}, ... ]
            Do NOT use markdown code blocks. Just the JSON array.
            If no items found, return [].
            """
            
            response = model.generate_content([full_prompt, image])
            text_response = response.text.strip()
            
            # Nettoyage markdown si présent
            if text_response.startswith("```json"):
                text_response = text_response[7:].strip()
            if text_response.startswith("```"):
                text_response = text_response[3:].strip()
            if text_response.endswith("```"):
                text_response = text_response[:-3].strip()
            
            data = json.loads(text_response)
            if isinstance(data, list):
                return data
            else:
                self._log(f"⚠️ Réponse Vision non-paramétrée (pas une liste): {str(data)[:100]}")
                return []
            
        except Exception as e:
            self._log(f"❌ Erreur Vision: {e}")
            return []

    def _scrape_leboncoin(self, url: str, query: str) -> List[Dict]:
        """
        Scraping spécifique pour LeBonCoin
        
        Args:
            url: URL complète de recherche
            query: Terme de recherche (informatif)
        
        Returns:
            Liste de dictionnaires avec les annonces
        """
        # Créer ou réutiliser une page
        if self.context.pages:
            self._log("Réutilisation de l'onglet existant (Persistent Context).")
            page = self.context.pages[0]
            # Fermer les onglets supplémentaires si présents
            for extra_page in self.context.pages[1:]:
                try:
                    extra_page.close()
                except:
                    pass
        else:
            self._log("Création d'un nouvel onglet.")
            page = self.context.new_page()
        # Note: Le stealth est appliqué au niveau du contexte maintenant
        
        results = []
        
        try:
            # Utilisation directe de l'URL fournie
            search_url = url
            if not search_url.startswith("http"):
                # Fallback si l'URL semble vide ou invalide, mais on privilégie l'URL brute
                 search_url = f"https://www.leboncoin.fr/recherche?text={query}"
            
            self._log(f"Navigation vers : {search_url}")
            
            # Navigation avec trace explicite
            self._log(f"⚡ Injection de l'URL pour navigation (après 2s) : {search_url}")
            time.sleep(2)
            
            # Navigation explicite vers l'URL cible
            try:
                self._log(f"🌐 Chargement de la page...")
                # Timeout augmenté à 2min pour laisser le temps de passer un captcha manuel si besoin
                response = page.goto(search_url, wait_until="networkidle", timeout=120000)
                if response:
                    self._log(f"✅ Page chargée (status: {response.status})")
                else:
                    self._log("⚠️ Navigation terminée sans response (possible si déjà sur la page)")
            except Exception as e:
                self._log(f"❌ Erreur de navigation: {e}")
                # Essayer navigation de secours avec wait_until moins strict
                try:
                    self._log("Tentative navigation de secours (domcontentloaded)...")
                    page.goto(search_url, wait_until="domcontentloaded", timeout=60000)
                except Exception as e2:
                    self._log(f"❌ Échec navigation de secours: {e2}")
                    raise
            
            self._log("Page chargée. Analyse du contenu...")
            
            # Simulation humaine pour éviter détection
            self._simulate_human_behavior(page)

            # Attendre que les résultats se chargent
            try:
                page.wait_for_selector('[data-qa-id="aditem_container"]', timeout=120000)
            except:
                self._log("⚠️ Timeout attente sélecteur LBC. Essai d'extraction immédiate.")
                # Essayer quand même d'extraire ce qui est disponible
            
            # Extraire les annonces
            ads = page.query_selector_all('[data-qa-id="aditem_container"]')
            self._log(f"Trouvé {len(ads)} annonces brutes sur la page.")
            
            for ad in ads[:20]:  # Limiter à 20 résultats
                try:
                    title_elem = ad.query_selector('[data-qa-id="aditem_title"]')
                    price_elem = ad.query_selector('[data-qa-id="aditem_price"]')
                    location_elem = ad.query_selector('[data-qa-id="aditem_location"]')
                    link_elem = ad.query_selector('a[href]')
                    image_elem = ad.query_selector('img')
                    
                    result = {
                        'title': title_elem.text_content().strip() if title_elem else "N/A",
                        'price': price_elem.text_content().strip() if price_elem else "N/A",
                        'location': location_elem.text_content().strip() if location_elem else "N/A",
                        'url': "https://www.leboncoin.fr" + link_elem.get_attribute('href') if link_elem else "N/A",
                        'image': image_elem.get_attribute('src') if image_elem else "N/A",
                        'scraped_at': datetime.now().isoformat()
                    }
                    
                    results.append(result)
                    
                except Exception as e:
                    self.logger.warning(f"Erreur extraction annonce: {e}")
                    continue
            
            # Plan B : Vision Scraping si aucun résultat CSS et Clé API présente
            if len(results) == 0 and self.llm_api_key:
                self._log("⚠️ Aucun résultat via CSS. Tentative de plan B: VISION SCRAPING 🧠")
                try:
                    # Capture de la zone visible (souvent suffisant pour les lazy loading)
                    screenshot = page.screenshot()
                    
                    vision_results = self._analyze_with_vision(
                        screenshot, 
                        "Analyse cette capture d'écran de liste d'annonces. "
                        "Extrais toutes les annonces visibles avec : titre, prix, localisation. "
                        "Ignore les publicités."
                    )
                    
                    if vision_results:
                        self._log(f"✅ Vision a trouvé {len(vision_results)} annonces !")
                        # Ajout métadonnées
                        for r in vision_results:
                            r['scraped_at'] = datetime.now().isoformat()
                            r['source'] = 'vision_llm'
                            if 'url' not in r: r['url'] = "N/A (Vision)"
                        results.extend(vision_results)
                    else:
                        self._log("❌ Vision n'a rien trouvé non plus.")

                except Exception as e:
                    self._log(f"❌ Échec du Vision Scraping: {e}")
            
        except Exception as e:
            error_str = str(e)
            if "Target page, context or browser has been closed" in error_str or "TargetClosedError" in error_str:
                self._log("⚠️ Navigateur fermé (ou crash) pendant le scraping. Retour des résultats partiels.")
                return results
            self.logger.error(f"Erreur scraping LeBonCoin: {e}")
            raise
        finally:
            page.close()
        
        return results
    
    def _scrape_generic(self, url: str, query: str) -> List[Dict]:
        """
        Scraping générique pour autres sites
        Utilise des sélecteurs communs
        
        Args:
            url: URL de base du site
            query: Requête de recherche
        
        Returns:
            Liste de résultats
        """
        # Créer ou réutiliser une page
        if self.context.pages:
            self._log("Réutilisation de l'onglet existant (Générique - Persistent Context).")
            page = self.context.pages[0]
            # Fermer les onglets supplémentaires si présents
            for extra_page in self.context.pages[1:]:
                try:
                    extra_page.close()
                except:
                    pass
        else:
            self._log("Création d'un nouvel onglet (Générique).")
            page = self.context.new_page()
        # Note: Le stealth est appliqué au niveau du contexte maintenant
        
        results = []
        
        try:
            # Utilisation directe de l'URL fournie
            search_url = url
            # Si l'URL ne semble pas complète et qu'il y a une query, on tente de construire
            # Mais la demande utilisateur est de privilégier l'URL brute
            if query and "q=" not in search_url and "?" not in search_url:
                 self._log("⚠️ URL brute utilisée sans paramètre de recherche (comportement demandé).")
            
            self._log(f"Navigation vers (Générique) : {search_url}")
            
            # Navigation avec trace explicite
            self._log(f"⚡ Injection de l'URL pour navigation (après 2s)...")
            time.sleep(2)

            page.goto(search_url, wait_until="networkidle", timeout=120000)
            
            # Attendre un peu pour le chargement dynamique
            page.wait_for_timeout(2000)
            
            # Simulation humaine
            self._simulate_human_behavior(page)
            
            self._log("Page chargée. Test des sélecteurs CSS...")
            
            # Essayer différents sélecteurs communs pour les résultats
            selectors = [
                'article',
                '.product',
                '.item',
                '.result',
                '[class*="product"]',
                '[class*="item"]',
                '[class*="card"]'
            ]
            
            items = []
            for selector in selectors:
                items = page.query_selector_all(selector)
                if len(items) > 0:
                    self._log(f"✅ Trouvé {len(items)} éléments avec le sélecteur: '{selector}'")
                    break
            
            if not items:
                self._log("⚠️ Aucun élément trouvé avec les sélecteurs génériques standard.")
                return []
            
            # Extraire les informations
            for item in items[:20]:  # Limiter à 20 résultats
                try:
                    # Essayer de trouver titre
                    title = None
                    for title_sel in ['h1', 'h2', 'h3', '.title', '[class*="title"]']:
                        title_elem = item.query_selector(title_sel)
                        if title_elem:
                            title = title_elem.text_content().strip()
                            break
                    
                    # Essayer de trouver prix
                    price = None
                    for price_sel in ['.price', '[class*="price"]', '[class*="amount"]']:
                        price_elem = item.query_selector(price_sel)
                        if price_elem:
                            price = price_elem.text_content().strip()
                            break
                    
                    # Essayer de trouver lien
                    link = None
                    link_elem = item.query_selector('a[href]')
                    if link_elem:
                        link = link_elem.get_attribute('href')
                        # Convertir en URL absolue si nécessaire
                        if link and not link.startswith('http'):
                            from urllib.parse import urljoin
                            link = urljoin(url, link)
                    
                    result = {
                        'title': title or "N/A",
                        'price': price or "N/A",
                        'url': link or "N/A",
                        'scraped_at': datetime.now().isoformat()
                    }
                    
                    # N'ajouter que si on a au moins un titre
                    if title:
                        results.append(result)
                    
                except Exception as e:
                    self.logger.warning(f"Erreur extraction item: {e}")
                    continue
            
        except Exception as e:
            error_str = str(e)
            if "Target page, context or browser has been closed" in error_str or "TargetClosedError" in error_str:
                self._log("⚠️ Navigateur fermé (ou crash) pendant le scraping générique. Retour des résultats partiels.")
                return results
            self.logger.error(f"Erreur scraping générique: {e}")
            raise
        finally:
            page.close()
        
        return results
    
    def _format_results(self, results: List[Dict]) -> str:
        """
        Formate les résultats pour l'affichage
        Compatible avec le format de AIScraper
        
        Args:
            results: Liste de résultats
        
        Returns:
            Texte formaté
        """
        if not results:
            return "❌ Aucun résultat trouvé."
        
        formatted = f"📊 **{len(results)} résultats trouvés** (Playwright)\n\n"
        
        for i, result in enumerate(results, 1):
            formatted += f"**{i}. {result.get('title', 'Sans titre')}**\n"
            
            if 'price' in result and result['price'] != "N/A":
                formatted += f"   💰 Prix : {result['price']}\n"
            
            if 'location' in result and result['location'] != "N/A":
                formatted += f"   📍 Lieu : {result['location']}\n"
            
            if 'url' in result and result['url'] != "N/A":
                formatted += f"   🔗 Lien : {result['url']}\n"
            
            formatted += "\n"
        
        return formatted.strip()
    
    def _save_results(self, url: str, query: str, extraction_prompt: str,
                     raw_results: List[Dict], formatted_results: str) -> Optional[str]:
        """
        Sauvegarde les résultats dans un fichier JSON
        
        Args:
            url: URL scrapée
            query: Requête de recherche
            extraction_prompt: Prompt d'extraction (pour compatibilité)
            raw_results: Résultats bruts
            formatted_results: Résultats formatés
        
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
                "provider": "playwright",
                "model": "chromium",
                "scraper_type": "playwright"
            }
            
            filepath = self.results_manager.save_result(data)
            self.logger.info(f"Résultats sauvegardés: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde des résultats: {e}")
            return None
