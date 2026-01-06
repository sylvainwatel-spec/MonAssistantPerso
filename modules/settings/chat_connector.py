import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from core.services.llm_service import LLMService

class ChatConnectorFrame(ctk.CTkFrame):
    """Page de configuration du connecteur LLM pour le chat.
    Refactored to support Provider + Dynamic Model."""
    
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app

        # --- Data Loading ---
        try:
            self.settings = self.app.data_manager.get_settings()
        except Exception as e:
            print(f"Error loading settings: {e}")
            self.settings = {}

        # Load Providers and Keys
        self.active_chat_provider = self.settings.get("chat_provider", "OpenAI")
        self.api_keys = self.settings.get("api_keys", {})
        self.endpoints = self.settings.get("endpoints", {})
        self.models = self.settings.get("models", {})
        
        # Simplified Provider List (No Models info here)
        self.providers = [
            "OpenAI",
            "Google Gemini",
            "Anthropic Claude",
            "Groq", # Llama 3 via Groq
            "Mistral AI",
            "Hugging Face",
            "DeepSeek",
            "IAKA (Interne)"
        ]
        
        # Define Free Providers (Totally free or Free Tier without Credit Card often)
        self.FREE_PROVIDERS = ["Groq", "Hugging Face", "IAKA (Interne)"]

        # UI State
        self.selected_provider = self.determine_selected_provider()
        self.sidebar_widgets = []
        self.log_textbox = None
        self.show_free_only = ctk.BooleanVar(value=False)

        # --- Layout ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # 1. Header (Top)
        self.create_header()

        # 2. Sidebar (Left) - List of Providers
        self.sidebar = ctk.CTkScrollableFrame(self, width=250, corner_radius=0, fg_color=("gray90", "gray15"))
        self.sidebar.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)

        # 3. Detail Panel (Right) - Configuration
        self.detail_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.detail_panel.grid(row=1, column=1, sticky="nsew", padx=20, pady=20)
        self.detail_panel.grid_columnconfigure(0, weight=1)

        # Initial Render
        self.refresh_sidebar()
        self.refresh_detail_panel()

    def determine_selected_provider(self):
        """Analyze active provider to determine selection, handling migration."""
        current = self.active_chat_provider
        # Map legacy names (e.g. 'OpenAI GPT-4o mini') to new Providers ('OpenAI')
        if "OpenAI" in current: return "OpenAI"
        if "Gemini" in current or "Google" in current: return "Google Gemini"
        if "Claude" in current or "Anthropic" in current: return "Anthropic Claude"
        if "Groq" in current: return "Groq"
        if "Mistral" in current: return "Mistral AI"
        if "DeepSeek" in current: return "DeepSeek"
        if "Hugging Face" in current: return "Hugging Face"
        if "IAKA" in current: return "IAKA (Interne)"
        return "OpenAI"

    def create_header(self):
        header = ctk.CTkFrame(self, height=60, corner_radius=0)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=10)

        btn_back = ctk.CTkButton(
            header,
            text="< Administration",
            width=140,
            height=32,
            fg_color=("gray70", "gray30"),
            corner_radius=16,
            command=self.app.show_admin,
        )
        btn_back.pack(side="left", padx=10)

        title = ctk.CTkLabel(header, text="💬 Connecteur LLM Chat", font=("Arial", 20, "bold"))
        title.pack(side="left", padx=20)

    def refresh_sidebar(self):
        for widget in self.sidebar_widgets:
            try: widget.destroy()
            except: pass
        self.sidebar_widgets = []
        
        # Filter Toggle
        toggle_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        toggle_frame.pack(fill="x", padx=10, pady=(10, 0))
        self.sidebar_widgets.append(toggle_frame)
        
        switch = ctk.CTkSwitch(
            toggle_frame, 
            text="Gratuits uniquement", 
            variable=self.show_free_only, 
            command=self.refresh_sidebar,
            font=("Arial", 11)
        )
        switch.pack(anchor="w")

        lbl = ctk.CTkLabel(
            self.sidebar,
            text="Fournisseurs",
            font=("Arial", 14, "bold"),
            text_color="gray60",
        )
        lbl.pack(pady=(10, 5), padx=10, anchor="w")
        self.sidebar_widgets.append(lbl)

        for provider in self.providers:
            # Filter logic
            if self.show_free_only.get() and provider not in self.FREE_PROVIDERS:
                continue
                
            # Check if this provider is effectively the active one
            # Logic: If active_chat_provider starts with this provider name or matches
            is_active = self.is_provider_active(provider)
            self.create_sidebar_item(provider, is_active)

    def is_provider_active(self, provider):
        """Check if provider matches active provider string (partial match for migration)."""
        # If active_chat_provider is "OpenAI" and provider is "OpenAI" -> True
        # If active_chat_provider is "OpenAI GPT-4o" and provider is "OpenAI" -> True
        p_clean = provider.split(" ")[0] # "OpenAI", "Google", "Mistral"
        return p_clean in self.active_chat_provider

    def create_sidebar_item(self, provider, is_active):
        is_selected = provider == self.selected_provider
        btn_color = ("gray80", "gray25") if is_selected else "transparent"
        
        item_frame = ctk.CTkFrame(self.sidebar, fg_color=btn_color, corner_radius=6)
        item_frame.pack(fill="x", padx=5, pady=2)
        self.sidebar_widgets.append(item_frame)
        
        item_frame.bind("<Button-1>", lambda e, p=provider: self.select_provider(p))
        
        # Indicator (Active)
        indicator_text = "●" if is_active else ""
        indicator = ctk.CTkLabel(item_frame, text=indicator_text, text_color="#4CAF50", font=("Arial", 16))
        indicator.pack(side="left", padx=(10, 5), pady=10)
        indicator.bind("<Button-1>", lambda e, p=provider: self.select_provider(p))

        # Name
        font_weight = "bold" if is_active else "normal"
        lbl_name = ctk.CTkLabel(item_frame, text=provider, font=("Arial", 13, font_weight))
        lbl_name.pack(side="left", padx=5)
        lbl_name.bind("<Button-1>", lambda e, p=provider: self.select_provider(p))
        
        # Free Bagde (Right aligned, before Active status)
        if provider in self.FREE_PROVIDERS:
            lbl_free = ctk.CTkLabel(
                item_frame, 
                text="GRATUIT", 
                font=("Arial", 9, "bold"), 
                text_color="white",
                fg_color="#4CAF50", # Green badge
                corner_radius=4,
                padx=4
            )
            lbl_free.pack(side="right", padx=(5, 5))
            lbl_free.bind("<Button-1>", lambda e, p=provider: self.select_provider(p))

        if is_active:
            lbl_status = ctk.CTkLabel(item_frame, text="ACTIF", font=("Arial", 10, "bold"), text_color="#2196F3")
            lbl_status.pack(side="right", padx=5)
            lbl_status.bind("<Button-1>", lambda e, p=provider: self.select_provider(p))

    def select_provider(self, provider):
        self.selected_provider = provider
        # Do NOT refresh sidebar here otherwise we lose scroll position or exact state sometimes, 
        # but needed to update selection highlight. 
        # Since list is small, it's fine.
        self.refresh_sidebar()
        self.refresh_detail_panel()

    def refresh_detail_panel(self):
        for widget in self.detail_panel.winfo_children(): widget.destroy()

        if not self.selected_provider: return

        # Header
        ctk.CTkLabel(self.detail_panel, text=self.selected_provider, font=("Arial", 24, "bold")).pack(anchor="w", pady=(0, 5))

        # --- API Key Section ---
        key_frame = ctk.CTkFrame(self.detail_panel)
        key_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(key_frame, text="Clé API", font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(15, 5))

        # Try to resolve key: first by exact provider name, then legacy map if needed
        current_key = self.get_provider_key(self.selected_provider)
        
        self.entry_key = ctk.CTkEntry(key_frame, width=400, show="*")
        self.entry_key.insert(0, current_key)
        self.entry_key.pack(side="left", padx=(20, 10), pady=5, fill="x", expand=True)

        self.btn_show_hide = ctk.CTkButton(key_frame, text="👁️", width=40, font=("Arial", 12), fg_color=("gray70", "gray30"), command=self.toggle_key_visibility)
        self.btn_show_hide.pack(side="left", padx=(0, 20))

        # --- Endpoint (IAKA/DeepSeek) --- 
        self.entry_endpoint = None
        if "IAKA" in self.selected_provider or "DeepSeek" in self.selected_provider or "OpenAI" in self.selected_provider: 
            # Allow base_url override for OpenAI compatible providers too if needed, but mainly IAKA
            ep_frame = ctk.CTkFrame(self.detail_panel)
            ep_frame.pack(fill="x", pady=10)
            ctk.CTkLabel(ep_frame, text="Endpoint URL", font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(15, 5))
            current_ep = self.endpoints.get(self.selected_provider, "")
            self.entry_endpoint = ctk.CTkEntry(ep_frame, width=400)
            self.entry_endpoint.insert(0, current_ep)
            self.entry_endpoint.pack(side="left", padx=20, pady=5, fill="x", expand=True)

        # --- Model Selector ---
        model_frame = ctk.CTkFrame(self.detail_panel)
        model_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(model_frame, text="Modèle", font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(15, 5))

        self.combo_model = ctk.CTkComboBox(model_frame, width=300)
        self.combo_model.pack(side="left", padx=(20, 10), pady=5)
        
        # Load saved model or default
        saved_model = self.models.get(self.selected_provider, "")
        if saved_model:
            self.combo_model.set(saved_model)
        else:
            self.combo_model.set("Cliquez sur Rafraîchir ->")

        btn_refresh = ctk.CTkButton(
            model_frame, 
            text="🔄 Rafraîchir", 
            width=100,
            command=self.fetch_models_list
        )
        btn_refresh.pack(side="left", padx=10)

        # Actions Bar
        action_frame = ctk.CTkFrame(self.detail_panel, fg_color="transparent")
        action_frame.pack(fill="x", pady=20)

        # Left Side: Test
        btn_test = ctk.CTkButton(
            action_frame, 
            text="Tester la connexion", 
            command=self.test_connection, 
            fg_color=("gray70", "gray30"), 
            hover_color=("gray60", "gray40"),
            width=140
        )
        btn_test.pack(side="left", padx=0)

        # Right Side: Application Actions
        if not self.is_provider_active(self.selected_provider):
            btn_activate = ctk.CTkButton(
                action_frame, 
                text="Définir comme Défaut", 
                command=self.set_active, 
                fg_color="#2196F3", 
                hover_color="#1976D2",
                width=160
            )
            btn_activate.pack(side="right", padx=(10, 0))

        btn_save = ctk.CTkButton(
            action_frame, 
            text="Enregistrer", 
            command=self.save_config, 
            fg_color="#4CAF50", 
            hover_color="#388E3C",
            width=120
        )
        btn_save.pack(side="right", padx=0)

        # Logs
        self.create_log_area()

    def get_provider_key(self, provider):
        """Retrieve key, handling legacy keys."""
        if provider in self.api_keys: return self.api_keys[provider]
        # Legacy fallback logic
        if "OpenAI" in provider:
             # Try finding any key starting with OpenAI
             for k in self.api_keys:
                 if "OpenAI" in k and self.api_keys[k]: return self.api_keys[k]
        return ""

    def create_log_area(self):
        logs_frame = ctk.CTkFrame(self.detail_panel, fg_color=("gray95", "gray20"))
        logs_frame.pack(fill="both", expand=True, pady=(20, 10))
        ctk.CTkLabel(logs_frame, text="📋 Logs", font=("Arial", 12, "bold")).pack(anchor="w", padx=15, pady=(10, 5))
        self.log_textbox = ctk.CTkTextbox(logs_frame, height=100, font=("Consolas", 10))
        self.log_textbox.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    def add_log(self, message, status="info"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        icons = {"success": "✅", "error": "❌", "info": "ℹ️"}
        log_entry = f"[{timestamp}] {icons.get(status, 'ℹ️')} {message}\n"
        self.log_textbox.insert("end", log_entry)
        self.log_textbox.see("end")

    def toggle_key_visibility(self):
        if self.entry_key.cget("show") == "*":
            self.entry_key.configure(show="")
            self.btn_show_hide.configure(text="🔒")
        else:
            self.entry_key.configure(show="*")
            self.btn_show_hide.configure(text="👁️")

    def fetch_models_list(self):
        """Call LLMService to get models."""
        api_key = self.entry_key.get().strip()
        if not api_key:
            messagebox.showerror("Erreur", "Veuillez entrer une clé API d'abord.")
            return

        self.add_log(f"Récupération des modèles pour {self.selected_provider}...", "info")
        
        kwargs = {}
        if self.entry_endpoint:
            kwargs['base_url'] = self.entry_endpoint.get().strip()
            
        models = LLMService.fetch_models(self.selected_provider, api_key, **kwargs)
        
        if models and not models[0].startswith("Erreur"):
            # Annotate Free Models
            display_models = []
            for m in models:
                is_free = False
                
                # Logic to identify free models
                if self.selected_provider in ["Groq", "Hugging Face", "IAKA (Interne)"]:
                    is_free = True
                elif "Gemini" in self.selected_provider and "flash" in m.lower():
                    is_free = True # Gemini Flash is free tier
                
                if is_free:
                    display_models.append(f"{m} (GRATUIT)")
                else:
                    display_models.append(m)
            
            self.combo_model.configure(values=display_models)
            self.combo_model.set(display_models[0])
            self.add_log(f"{len(models)} modèles trouvés.", "success")
        else:
            self.add_log(f"Erreur récupération: {models[0]}", "error")
            # If error, maybe allow manual entry or keep previous
            
    def save_config(self):
        api_key = self.entry_key.get().strip()
        # Clean model name (remove Free annotation)
        model = self.combo_model.get().replace(" (GRATUIT)", "").strip()
        
        self.api_keys[self.selected_provider] = api_key
        self.models[self.selected_provider] = model
        
        if self.entry_endpoint:
            self.endpoints[self.selected_provider] = self.entry_endpoint.get().strip()
            
        self.save_to_manager()
        self.add_log(f"Configuration sauvegardée pour {self.selected_provider}.", "success")

    def set_active(self):
        self.save_config() # Ensure saved
        self.active_chat_provider = self.selected_provider
        self.save_to_manager()
        self.refresh_sidebar()
        self.refresh_detail_panel()
        messagebox.showinfo("Succès", f"{self.selected_provider} est le fournisseur actif.")
        self.add_log(f"Activé: {self.selected_provider} ({self.models.get(self.selected_provider)})", "success")

    def save_to_manager(self):
        # We save the 'active_chat_provider' as the Provider Name (e.g. "OpenAI")
        # Services must look up models[provider]
        self.app.data_manager.save_configuration(
            chat_provider=self.active_chat_provider,
            scrapegraph_provider=self.settings.get("scrapegraph_provider", "OpenAI"),
            api_keys=self.api_keys,
            endpoints=self.endpoints,
            models=self.models # IMPORTANT: New arg
        )

    def test_connection(self):
        api_key = self.entry_key.get().strip()
        # Clean model name (remove Free annotation)
        model = self.combo_model.get().replace(" (GRATUIT)", "").strip()
        
        kwargs = {}
        if self.entry_endpoint:
            kwargs['base_url'] = self.entry_endpoint.get().strip()
            
        self.add_log("Test de connexion...", "info")
        success, msg = LLMService.generate_response(
            self.selected_provider, 
            api_key, 
            [{"role":"user", "content":"Hello"}],
            model=model,
            **kwargs
        )
        
        self.add_log(f"Test Call - Provider: {self.selected_provider}, Model: {model}, Kwargs: {kwargs}", "info")
        print(f"[DEBUG] ChatConnector Test - Provider: {self.selected_provider}, Model: {model}, Kwargs: {kwargs}")  # Debug Console
        
        success, msg = LLMService.generate_response(
            self.selected_provider, 
            api_key, 
            [{"role":"user", "content":"Hello"}],
            model=model,
            **kwargs
        )
        
        if success:
            self.add_log(f"Test réussi: {msg[:50]}...", "success")
            messagebox.showinfo("Succès", f"Connexion OK !\nModèle: {model}")
        else:
            self.add_log(f"Echec: {msg}", "error")
            messagebox.showerror("Erreur", f"Echec: {msg}")
