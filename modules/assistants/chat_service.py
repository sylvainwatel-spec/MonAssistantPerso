from core.services.llm_service import LLMService as LLMConnectionTester
from utils.scraper_factory import ScraperFactory
from utils.results_manager import ResultsManager
import os
import datetime
import logging
import threading

# Import provider libraries (lazy imports within methods preferred if they are optional, 
# but for service we can import them at top level or inside methods as in original code)

class ChatService:
    def __init__(self, data_manager, assistant_data):
        self.data_manager = data_manager
        self.assistant = assistant_data
        self.assistant_id = str(self.assistant.get('id', 'default'))
        self.logger = logging.getLogger(__name__)

    def test_connections(self, log_callback=None):
        """
        Tests connections to LLM providers (chat and scraping).
        calls log_callback(message) for status updates.
        """
        if not log_callback:
            log_callback = lambda x: None

        settings = self.data_manager.get_settings()
        
        # Test 1: Provider Chat
        chat_provider = self.assistant.get('provider', 'OpenAI GPT-4o mini')
        chat_api_key = settings.get('api_keys', {}).get(chat_provider)
        
        log_callback(f"🔍 Test de connexion au LLM Chat ({chat_provider})...")
        
        if not chat_api_key:
            log_callback(f"⚠️ Aucune clé API configurée pour {chat_provider}")
        else:
            endpoint = None
            model_name = None
            if "IAKA" in chat_provider:
                endpoint = settings.get('endpoints', {}).get(chat_provider)
                model_name = settings.get("models", {}).get(chat_provider)
            
            success, message = LLMConnectionTester.test_provider(chat_provider, chat_api_key, base_url=endpoint, model=model_name)
            
            if success:
                log_callback(f"✅ LLM Chat: Connexion réussie à {chat_provider}")
            else:
                if "quota" in message.lower() or "429" in message:
                    error_summary = "Quota dépassé"
                elif "401" in message or "403" in message or "invalid" in message.lower():
                    error_summary = "Clé API invalide"
                elif "404" in message or "not found" in message.lower():
                    error_summary = "Modèle non disponible"
                else:
                    error_summary = "Erreur de connexion"
                
                log_callback(f"❌ LLM Chat: {error_summary} ({chat_provider})")
        
        # Test 2: Provider ScrapeGraph (si URL cible configurée)
        if self.assistant.get('target_url'):
            sg_provider = settings.get("scrapegraph_provider", "OpenAI GPT-4o mini")
            sg_api_key = settings.get("api_keys", {}).get(sg_provider)
            
            log_callback(f"🔍 Test de connexion au LLM Scraping ({sg_provider})...")
            
            if not sg_api_key:
                log_callback(f"⚠️ Aucune clé API configurée pour {sg_provider}")
            else:
                endpoint = None
                model_name = None
                if "IAKA" in sg_provider:
                    endpoint = settings.get('endpoints', {}).get(sg_provider)
                    model_name = settings.get("models", {}).get(sg_provider)
                
                success, message = LLMConnectionTester.test_provider(sg_provider, sg_api_key, base_url=endpoint, model=model_name)
                
                if success:
                    log_callback(f"✅ LLM Scraping: Connexion réussie à {sg_provider}")
                else:
                    if "quota" in message.lower() or "429" in message:
                        error_summary = "Quota dépassé"
                    elif "401" in message or "403" in message or "invalid" in message.lower():
                        error_summary = "Clé API invalide"
                    elif "404" in message or "not found" in message.lower():
                        error_summary = "Modèle non disponible"
                    else:
                        error_summary = "Erreur de connexion"
                    
                    log_callback(f"❌ LLM Scraping: {error_summary} ({sg_provider})")
        
        log_callback("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    def generate_response(self, user_message, system_prompt, system_msg_callback=None):
        """
        Generates a response from the LLM.
        Result is a dict: {'success': bool, 'text': str, 'error': str}
        """
        try:
            settings = self.data_manager.get_settings()
            provider = self.assistant.get('provider', 'OpenAI GPT-4o mini')
            api_key = settings.get('api_keys', {}).get(provider)
            
            if not api_key:
                available_keys = list(settings.get('api_keys', {}).keys())
                error_msg = (
                    f"⚠️ **Clé API invalide**\n"
                    f"La clé API est incorrecte ou a expiré.\n"
                    f"Solution : Vérifiez la clé dans la page Administration.\n\n"
                    f"Debug Info:\n"
                    f"- Provider de l'assistant : '{provider}'\n"
                    f"- Clés disponibles : {available_keys}"
                )
                return {'success': False, 'error': error_msg}

            # RAG Support
            kb_id = self.assistant.get('knowledge_base_id')
            if kb_id and kb_id != "None":
                if system_msg_callback: system_msg_callback(f"🧠 Utilisation de la base de connaissances (RAG)...")
                
                messages_for_llm = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ]
                
                success, response_text = LLMConnectionTester.generate_response_with_rag(
                    provider_name=provider,
                    api_key=api_key,
                    messages=messages_for_llm,
                    kb_id=kb_id,
                    base_url=settings.get('endpoints', {}).get(provider),
                    model=settings.get("models", {}).get(provider)
                )
                
                if not success:
                    raise Exception(f"RAG Error: {response_text}")
                
                return {'success': True, 'text': response_text, 'api_key': api_key}
            
            else:
                # Standard Generation
                response_text = ""
                # IMPORTANT : Vérifier "Hugging Face" AVANT "Mistral"
                if "OpenAI" in provider:
                    response_text = self._call_openai(api_key, system_prompt, user_message)
                elif "Gemini" in provider:
                    response_text = self._call_gemini(api_key, system_prompt, user_message)
                elif "Claude" in provider:
                    response_text = self._call_claude(api_key, system_prompt, user_message)
                elif "Llama" in provider or "Groq" in provider:
                    response_text = self._call_groq(api_key, system_prompt, user_message)
                elif "Hugging Face" in provider:
                    response_text = self._call_huggingface(api_key, system_prompt, user_message)
                elif "Mistral" in provider:
                    response_text = self._call_mistral(api_key, system_prompt, user_message)
                elif "DeepSeek-VL" in provider:
                    response_text = self._call_deepseek_vl(api_key, system_prompt, user_message)
                elif "DeepSeek" in provider:
                     response_text = self._call_openai_compatible(api_key, "https://api.deepseek.com", system_prompt, user_message)
                elif "IAKA" in provider:
                    endpoint = settings.get('endpoints', {}).get(provider)
                    model_name = settings.get("models", {}).get(provider, "mistral-small")
                    if not endpoint:
                        raise Exception(f"Endpoint URL non configuré pour {provider}.")
                    response_text = self._call_iaka(api_key, endpoint, system_prompt, user_message, model_name)
                else:
                    response_text = f"Provider {provider} non supporté pour le moment."
                
                return {'success': True, 'text': response_text, 'api_key': api_key}

        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "402" in error_msg or "quota" in error_msg.lower() or "payment" in error_msg.lower():
                friendly_msg = (
                    "⚠️ **Quota API dépassé (ou Payant)**\n"
                    "La limite d'utilisation gratuite pour ce modèle est atteinte (Erreur 402/429).\n"
                    "Solution : Changez de modèle ou de fournisseur (ex: Groq, Gemini) dans les paramètres de l'assistant.\n\n"
                    f"Erreur technique : {error_msg}"
                )
                return {'success': False, 'error': friendly_msg}
            elif "401" in error_msg or ("invalid" in error_msg.lower() and "api" in error_msg.lower()):
                friendly_msg = (
                    "⚠️ **Clé API invalide**\n"
                    "La clé API est incorrecte ou a expiré.\n"
                    "Solution : Vérifiez la clé dans la page Administration.\n\n"
                    f"Erreur technique : {error_msg}"
                )
                return {'success': False, 'error': friendly_msg}
            else:
                return {'success': False, 'error': f"❌ Erreur technique : {error_msg}"}

    def process_response_action(self, response_text, api_key, system_prompt, original_user_message, system_msg_callback=None):
        """
        Checks if response contains an action (Search) and executes it if needed.
        Returns generator yielding status updates (str) and finally the result (dict).
        """
        if not system_msg_callback:
            system_msg_callback = lambda x: None

        if "ACTION: SEARCH" in response_text:
            parts = response_text.split("ACTION: SEARCH")
            intro_text = parts[0].strip()
            query = parts[1].strip()
            
            # Yield intro text if any
            yield {'type': 'text', 'content': intro_text} if intro_text else None
            
            system_msg_callback(f"🔎 Recherche en cours sur {self.assistant.get('target_url')} : '{query}'...")
            yield {'type': 'system', 'content': f"🔎 Recherche en cours sur {self.assistant.get('target_url')} : '{query}'..."}
            
            # Scraper logic
            url_instructions = self.assistant.get('url_instructions', '')
            if not url_instructions:
                msg = "⚠️ Aucune instruction d'extraction configurée."
                system_msg_callback(msg)
                yield {'type': 'system', 'content': msg}
                return

            system_msg_callback(f"📝 Instructions: {url_instructions[:50]}...")
            
            try:
                # Determine scraping solution
                settings = self.data_manager.get_settings()
                global_default = settings.get("scraping_solution", "scrapegraphai")
                scraping_solution = self.assistant.get("scraping_solution", global_default)
                
                # Setup Log callback
                def log_scraper(msg):
                   system_msg_callback(f"🕸️ {msg}")

                scraper_params = {
                    "assistant_id": self.assistant_id,
                    "assistant_name": self.assistant.get('name', 'Unknown'),
                    "log_callback": log_scraper
                }
                
                if scraping_solution == "scrapegraphai":
                    sg_provider = settings.get("scrapegraph_provider", "OpenAI GPT-4o mini")
                    sg_api_key = settings.get("api_keys", {}).get(sg_provider)
                    
                    if not sg_api_key:
                        raise Exception("No scraping API key")

                    provider_code = "openai"
                    if "Gemini" in sg_provider: provider_code = "google"
                    elif "Groq" in sg_provider: provider_code = "groq"
                    
                    model_code = "gpt-4o-mini"
                    if "Gemini" in sg_provider: model_code = "gemini-2.0-flash-exp"
                    elif "Llama" in sg_provider: model_code = "llama-3.1-8b-instant"
                    
                    system_msg_callback(f"🤖 Scraping avec {sg_provider}...")
                    scraper_params.update({
                        "api_key": sg_api_key,
                        "model": model_code,
                        "provider": provider_code
                    })
                else:
                    scraping_browser = settings.get("scraping_browser", "firefox")
                    system_msg_callback(f"🎭 Scraping avec Playwright ({scraping_browser})...")
                    scraper_params["headless"] = not settings.get("visible_mode", False)
                    scraper_params["browser_type"] = scraping_browser
                    
                    api_keys = settings.get("api_keys", {})
                    gemini_key = next((v for k, v in api_keys.items() if "Gemini" in k or "Google" in k), None)
                    if gemini_key:
                        scraper_params["llm_api_key"] = gemini_key
                        scraper_params["llm_model"] = "gemini-2.0-flash-exp"

                scraper = ScraperFactory.create_scraper(scraping_solution, **scraper_params)
                search_results, results_filepath = scraper.search(
                    url=self.assistant.get('target_url'),
                    query=query,
                    extraction_prompt=url_instructions
                )
                
                if results_filepath:
                    filename = os.path.basename(results_filepath)
                    system_msg_callback(f"✅ Résultats sauvegardés: {filename}")
                    
                    rm = ResultsManager()
                    loaded_results = rm.load_result(results_filepath)
                    if loaded_results:
                         results_text = loaded_results.get('results', 'Aucun résultat')
                         
                         # Truncate logic
                         if len(results_text) > 5000:
                             results_text = results_text[:5000] + f"\n\n[... Tronqué {len(results_text)} chars ...]"
                             
                         system_msg_callback("🤖 Analyse des résultats en cours...")
                         
                         analysis_prompt = f"Les résultats du scraping ont été récupérés avec succès.\n\nREQUÊTE : {query}\nURL : {self.assistant.get('target_url')}\n\nRÉSULTATS :\n{results_text}\n\nINSTRUCTIONS :\nAnalyse ces résultats. Structure ta réponse en 2 parties:\nPartie 1 : Analyse détaillée\nPartie 2 : Synthèse à exporter (Tableau Markdown uniquement)."
                         
                         new_user_message = analysis_prompt
                    else:
                         new_user_message = f"{original_user_message}\n\n[RÉSULTATS DE LA RECHERCHE]:\n{search_results[:4000]}"
                else:
                    new_user_message = f"{original_user_message}\n\n[RÉSULTATS DE LA RECHERCHE]:\n{search_results[:4000]}"
                
                # Recursive call for analysis
                final_res = self.generate_response(new_user_message, system_prompt)
                if final_res['success']:
                    yield {'type': 'text', 'content': final_res['text']}
                else:
                    yield {'type': 'error', 'content': final_res['error']}

            except Exception as e:
                err = f"❌ Erreur lors du scraping IA: {str(e)}"
                system_msg_callback(err)
                yield {'type': 'error', 'content': err}
        else:
             # Just return original text if no action
             yield {'type': 'text', 'content': response_text}


    # --- Provider Implementation Methods (Copied & Adapted) ---

    def _call_openai(self, api_key, system_prompt, user_message):
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_message}],
            max_tokens=4000, temperature=0.7
        )
        return response.choices[0].message.content

    def _call_openai_compatible(self, api_key, base_url, system_prompt, user_message):
        from openai import OpenAI
        client = OpenAI(api_key=api_key, base_url=base_url)
        model_to_use = "gpt-3.5-turbo"
        try:
            models = client.models.list()
            if models.data: model_to_use = models.data[0].id
        except: pass
        response = client.chat.completions.create(
            model=model_to_use,
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_message}],
            max_tokens=4000, temperature=0.7
        )
        return response.choices[0].message.content

    def _call_iaka(self, api_key, base_url, system_prompt, user_message, model_name="mistral-small"):
        from openai import OpenAI
        code_model = model_name if model_name else "mistral-small"
        clean_base_url = base_url.rstrip('/')
        full_url = clean_base_url if "/v1" in clean_base_url else f"{clean_base_url}/{code_model}/v1"
        client = OpenAI(api_key=api_key, base_url=full_url)
        response = client.chat.completions.create(
            model=code_model,
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_message}],
            temperature=0.7, max_tokens=4000
        )
        return response.choices[0].message.content

    def _call_gemini(self, api_key, system_prompt, user_message):
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods and 'preview' not in m.name.lower()]
        if not available_models: raise Exception("Aucun modèle Gemini disponible")
        flash_models = [m for m in available_models if 'flash' in m.lower()]
        model_name = flash_models[0] if flash_models else available_models[0]
        model = genai.GenerativeModel(model_name)
        return model.generate_content(f"{system_prompt}\n\nUtilisateur : {user_message}").text

    def _call_claude(self, api_key, system_prompt, user_message):
        from anthropic import Anthropic
        client = Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-opus-4-20250514", max_tokens=4000, system=system_prompt,
            messages=[{"role": "user", "content": user_message}]
        )
        return response.content[0].text

    def _call_groq(self, api_key, system_prompt, user_message):
        from groq import Groq
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_message}],
            max_tokens=4000, temperature=0.7
        )
        return response.choices[0].message.content

    def _call_mistral(self, api_key, system_prompt, user_message):
        from mistralai import Mistral
        client = Mistral(api_key=api_key)
        response = client.chat.complete(
            model="mistral-small-latest",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_message}],
            max_tokens=4000
        )
        return response.choices[0].message.content

    def _call_deepseek_vl(self, api_key, system_prompt, user_message):
        from openai import OpenAI
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        response = client.chat.completions.create(
            model="deepseek-vl",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_message}],
            max_tokens=4000, temperature=0.7
        )
        return response.choices[0].message.content

    def _call_huggingface(self, api_key, system_prompt, user_message):
        from huggingface_hub import InferenceClient
        import time
        client = InferenceClient(token=api_key.strip() if api_key else "")
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_message}]
        for attempt in range(3):
            try:
                response = client.chat_completion(
                    messages=messages, model="Qwen/Qwen2.5-72B-Instruct", max_tokens=4000, temperature=0.7
                )
                return response.choices[0].message.content
            except Exception as e:
                if "504" in str(e) or "503" in str(e) or "429" in str(e):
                    time.sleep(2 * (attempt + 1))
                    continue
                raise e
