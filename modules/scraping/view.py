import customtkinter as ctk
import threading
import time


class ScrapingFrame(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.build_ui()

    def build_ui(self):
        # 1. Header
        header = ctk.CTkFrame(self, height=60, corner_radius=0)
        header.pack(fill="x", padx=20, pady=10)
        
        btn_back = ctk.CTkButton(
            header,
            text="< Accueil",
            width=100,
            height=32,
            fg_color=("gray70", "gray30"),
            corner_radius=16,
            command=self.app.show_home,
        )
        btn_back.pack(side="left", padx=10, pady=10)
        
        title = ctk.CTkLabel(header, text="🕸️ Scraping Tool", font=("Arial", 20, "bold"))
        title.pack(side="left", padx=20)

        # 2. Main Content (Grid 2 columns)
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=10)
        content.grid_columnconfigure(0, weight=1) # Left: Config
        content.grid_columnconfigure(1, weight=2) # Right: Chat
        content.grid_rowconfigure(0, weight=1)

        # --- Left Column: Configuration ---
        config_frame = ctk.CTkFrame(content)
        config_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        ctk.CTkLabel(config_frame, text="Paramètres", font=("Arial", 16, "bold")).pack(pady=20)
        
        # Display Active Solution
        settings = self.app.data_manager.get_settings()
        active_solution = settings.get("scraping_solution", "scrapegraphai")  # Default to ScrapeGraphAI
        
        solution_text = "ScrapeGraphAI" if active_solution == "scrapegraphai" else "Playwright + LLM Vision"
        solution_color = "#4CAF50" if active_solution == "scrapegraphai" else "#2196F3"
        
        lbl_solution = ctk.CTkLabel(
            config_frame, 
            text=f"Moteur : {solution_text}", 
            font=("Arial", 12, "bold"),
            text_color=solution_color
        )
        lbl_solution.pack(pady=(0, 10))
        
        # URL Input
        lbl_url = ctk.CTkLabel(config_frame, text="URL Cible :", font=("Arial", 12, "bold"))
        lbl_url.pack(anchor="w", padx=20, pady=(10, 5))
        
        self.entry_url = ctk.CTkEntry(config_frame, placeholder_text="https://example.com")
        self.entry_url.pack(fill="x", padx=20, pady=5)
        
        # Options Input
        lbl_options = ctk.CTkLabel(config_frame, text="Champs et Options :", font=("Arial", 12, "bold"))
        lbl_options.pack(anchor="w", padx=20, pady=(15, 5))
        
        self.txt_options = ctk.CTkTextbox(config_frame, height=200)
        self.txt_options.pack(fill="x", padx=20, pady=5)
        self.txt_options.insert("1.0", "{\n  \"fields\": [\"title\", \"price\"],\n  \"format\": \"json\"\n}")

        # Start Button
        self.btn_start = ctk.CTkButton(
            config_frame, 
            text="Lancer le Scraping",
            font=("Arial", 14, "bold"),
            height=40,
            fg_color="#FF5722",
            hover_color="#E64A19",
            command=self.start_scraping
        )
        self.btn_start.pack(pady=30, padx=20)

        # --- Right Column: Chat ---
        chat_frame = ctk.CTkFrame(content)
        chat_frame.grid(row=0, column=1, sticky="nsew")
        chat_frame.grid_rowconfigure(0, weight=1)
        chat_frame.grid_columnconfigure(0, weight=1)

        # Chat Display
        self.chat_display = ctk.CTkTextbox(chat_frame, state="disabled", font=("Consolas", 12))
        self.chat_display.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Input Area
        input_area = ctk.CTkFrame(chat_frame, height=50)
        input_area.grid(row=3, column=0, sticky="ew", padx=10, pady=10) # Moved to row 3 to make space for progress bar at row 2
        
        self.msg_entry = ctk.CTkEntry(input_area, placeholder_text="Interagissez avec les résultats...")
        self.msg_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.msg_entry.bind("<Return>", self.send_message)
        
        self.btn_send = ctk.CTkButton(input_area, text="Envoyer", width=80, command=self.send_message)
        self.btn_send.pack(side="right")
        
        # Progress Bar (initially hidden)
        self.progress_bar = ctk.CTkProgressBar(
            chat_frame, 
            mode="indeterminate",
            height=8, 
            corner_radius=4,
            progress_color=("#4CAF50", "#4CAF50"),
            fg_color=("gray85", "gray25")
        )
        # We will grid it when needed, e.g. between chat and input
        
        # Initial Message
        self.append_chat("System", "Bienvenue dans l'outil de scraping. Configurez l'URL et lancez l'extraction.")

    def start_scraping(self):
        url = self.entry_url.get()
        options = self.txt_options.get("1.0", "end").strip()
        
        if not url:
            self.append_chat("System", "❌ Erreur: Veuillez saisir une URL.")
            return

        self.btn_start.configure(state="disabled", text="Scraping en cours...")
        self.entry_url.configure(state="disabled")
        
        # Show Progress Bar
        self.progress_bar.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        self.progress_bar.start()

        self.append_chat("System", f"🚀 Démarrage du scraping sur : {url}")
        
        # Run in thread
        thread = threading.Thread(target=self._run_scraping_thread, args=(url, options))
        thread.daemon = True
        thread.start()

    def _run_scraping_thread(self, url, options):
        try:
            self.after(0, lambda: self.append_chat("System", "⏳ Initialisation du scraper..."))
            
            from utils.scraper_factory import ScraperFactory
            import os
            
            settings = self.app.data_manager.get_settings()
            scraping_solution = settings.get("scraping_solution", "scrapegraphai")
            
            # Helper for logging in thread
            def log_callback(msg):
                try:
                    self.after(0, lambda: self.append_chat("System", f"🕸️ {msg}"))
                except:
                    pass

            scraper_params = {
                "assistant_id": "standalone_tool",
                "assistant_name": "Scraping Tool",
                "log_callback": log_callback
            }

            # --- Configuration specific to solution ---
            if scraping_solution == "scrapegraphai":
                sg_provider = settings.get("scrapegraph_provider", "OpenAI GPT-4o mini")
                sg_api_key = settings.get("api_keys", {}).get(sg_provider)
                
                if not sg_api_key:
                     raise ValueError(f"Aucune clé API configurée pour {sg_provider}")
                
                # Provider Mapping
                provider_code = "openai"
                if "Gemini" in sg_provider:
                    provider_code = "google"
                elif "Groq" in sg_provider:
                    provider_code = "groq"
                
                # Model Mapping
                model_code = "gpt-4o-mini"
                if "Gemini" in sg_provider:
                    model_code = "gemini-2.0-flash-exp"
                elif "Llama" in sg_provider:
                    model_code = "llama-3.1-8b-instant"

                scraper_params.update({
                    "api_key": sg_api_key,
                    "model": model_code,
                    "provider": provider_code
                })

            else: # Playwright
                 scraping_browser = settings.get("scraping_browser", "firefox")
                 scraper_params["headless"] = not settings.get("visible_mode", False)
                 scraper_params["browser_type"] = scraping_browser
                 
                 # Vision Fallback (Gemini)
                 api_keys = settings.get("api_keys", {})
                 gemini_key = next((v for k, v in api_keys.items() if "Gemini" in k or "Google" in k), None)
                 
                 if gemini_key:
                     scraper_params["llm_api_key"] = gemini_key
                     scraper_params["llm_model"] = "gemini-2.0-flash-exp"

            # --- Execution ---
            self.after(0, lambda: self.append_chat("System", f"🚀 Lancement de {scraping_solution}..."))
            
            scraper = ScraperFactory.create_scraper(scraping_solution, **scraper_params)
            
            # Using 'options' as the extraction instruction/prompt
            # Passing 'options' as query too, as simple scrapers might use it as a general prompt
            search_results, results_filepath = scraper.search(
                url=url, 
                query=options, 
                extraction_prompt=options
            )
            
            self.after(0, lambda: self.append_chat("System", "✅ Scraping terminé !"))
            
            # Display Results (Truncated)
            display_text = str(search_results)
            if len(display_text) > 3000:
                display_text = display_text[:3000] + "\n\n[... Résultats tronqués pour l'affichage ...]"
                
            self.after(0, lambda: self.append_chat("Résultats", display_text))
            
            if results_filepath:
                 filename = os.path.basename(results_filepath)
                 self.after(0, lambda: self.append_chat("System", f"📁 Sauvegardé dans : {filename}"))
                 # Could automatically open/load it, but let's stick to display
            
        except Exception as e:
            self.after(0, lambda: self.append_chat("System", f"❌ Erreur: {e}"))
            
        finally:
            self.after(0, self._on_scraping_complete)

    def _on_scraping_complete(self):
        self.progress_bar.stop()
        self.progress_bar.grid_forget()
        self.btn_start.configure(state="normal", text="Lancer le Scraping")
        self.entry_url.configure(state="normal")

    def send_message(self, event=None):
        msg = self.msg_entry.get().strip()
        if not msg:
            return
            
        self.append_chat("Vous", msg)
        self.msg_entry.delete(0, "end")
        # Placeholder for chat response logic
        # self.append_chat("Assistant", "Réponse simulée...")

    def append_chat(self, sender, text):
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", f"\n[{sender}]: {text}\n")
        self.chat_display.see("end")
        self.chat_display.configure(state="disabled")
