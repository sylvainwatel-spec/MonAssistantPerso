import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from utils.llm_connector import LLMConnectionTester

class AdminFrame(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app

        # --- Data Loading ---
        try:
            self.settings = self.app.data_manager.get_settings()
        except Exception as e:
            print(f"Error loading settings: {e}")
            self.settings = {"current_provider": "OpenAI GPT-4o mini", "api_keys": {}}

        self.active_provider = self.settings.get("current_provider", "OpenAI GPT-4o mini")
        self.api_keys = self.settings.get("api_keys", {})

        # List of supported LLMs
        self.llm_options = [
            "Google Gemini 1.5 Flash",
            "OpenAI GPT-4o mini",
            "Anthropic Claude 3 Haiku",
            "Meta Llama 3 (via Groq)",
            "Mistral NeMo"
        ]

        # UI State
        self.selected_provider = self.active_provider
        
        # Log textbox reference
        self.log_textbox = None

        # --- Layout ---
        self.grid_columnconfigure(1, weight=1)  # Right panel expands
        self.grid_rowconfigure(1, weight=1)    # Content area expands

        # 1. Header (Top)
        self.create_header()

        # 2. Sidebar (Left) - List of LLMs
        self.sidebar = ctk.CTkScrollableFrame(self, width=250, corner_radius=0, fg_color=("gray90", "gray15"))
        self.sidebar.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)

        # 3. Detail Panel (Right) - Configuration
        self.detail_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.detail_panel.grid(row=1, column=1, sticky="nsew", padx=20, pady=20)
        self.detail_panel.grid_columnconfigure(0, weight=1)

        # Track widgets for safe clearing
        self.sidebar_widgets = []

        # Initial Render
        self.refresh_sidebar()
        self.refresh_detail_panel()

    def create_header(self):
        header = ctk.CTkFrame(self, height=60, corner_radius=0)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=10)

        btn_back = ctk.CTkButton(
            header,
            text="< Accueil",
            width=100,
            height=32,
            fg_color=("#3B8ED0", "#1F6AA5"),
            corner_radius=16,
            command=self.app.show_home,
        )
        btn_back.pack(side="left", padx=10)

        title = ctk.CTkLabel(header, text="Administration & Modèles", font=("Arial", 20, "bold"))
        title.pack(side="left", padx=20)

    def refresh_sidebar(self):
        # Clear existing widgets safely
        for widget in self.sidebar_widgets:
            try:
                widget.destroy()
            except:
                pass
        self.sidebar_widgets = []

        lbl = ctk.CTkLabel(
            self.sidebar,
            text="Modèles Disponibles",
            font=("Arial", 14, "bold"),
            text_color="gray60",
        )
        lbl.pack(pady=(10, 5), padx=10, anchor="w")
        self.sidebar_widgets.append(lbl)

        for provider in self.llm_options:
            self.create_sidebar_item(provider)

    def create_sidebar_item(self, provider):
        is_active = provider == self.active_provider
        is_selected = provider == self.selected_provider

        btn_color = ("gray80", "gray25") if is_selected else "transparent"
        item_frame = ctk.CTkFrame(self.sidebar, fg_color=btn_color, corner_radius=6)
        item_frame.pack(fill="x", padx=5, pady=2)
        self.sidebar_widgets.append(item_frame)

        item_frame.bind("<Button-1>", lambda e, p=provider: self.select_provider(p))
        item_frame.grid_columnconfigure(1, weight=1)

        indicator_text = "●" if is_active else ""
        indicator = ctk.CTkLabel(
            item_frame,
            text=indicator_text,
            text_color="#4CAF50",
            font=("Arial", 16),
        )
        indicator.grid(row=0, column=0, padx=(10, 5), pady=10)
        indicator.bind("<Button-1>", lambda e, p=provider: self.select_provider(p))

        font_weight = "bold" if is_active else "normal"
        lbl_name = ctk.CTkLabel(item_frame, text=provider, font=("Arial", 13, font_weight))
        lbl_name.grid(row=0, column=1, sticky="w", padx=5)
        lbl_name.bind("<Button-1>", lambda e, p=provider: self.select_provider(p))

        if is_active:
            lbl_status = ctk.CTkLabel(
                item_frame,
                text="ACTIF",
                font=("Arial", 10, "bold"),
                text_color="#4CAF50",
            )
            lbl_status.grid(row=0, column=2, padx=10)
            lbl_status.bind("<Button-1>", lambda e, p=provider: self.select_provider(p))

    def select_provider(self, provider):
        self.selected_provider = provider
        self.refresh_sidebar()
        self.refresh_detail_panel()

    def refresh_detail_panel(self):
        # Clear existing widgets
        for widget in self.detail_panel.winfo_children():
            widget.destroy()

        if not self.selected_provider:
            return

        # Header
        ctk.CTkLabel(
            self.detail_panel,
            text=self.selected_provider,
            font=("Arial", 24, "bold"),
        ).pack(anchor="w", pady=(0, 5))

        # API Key Section
        key_frame = ctk.CTkFrame(self.detail_panel)
        key_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(
            key_frame,
            text="Clé API",
            font=("Arial", 12, "bold"),
        ).pack(anchor="w", padx=20, pady=(15, 5))

        current_key = self.api_keys.get(self.selected_provider, "")
        self.entry_key = ctk.CTkEntry(key_frame, width=400, show="*")
        self.entry_key.insert(0, current_key)
        self.entry_key.pack(side="left", padx=(20, 10), pady=5, fill="x", expand=True)

        self.btn_show_hide = ctk.CTkButton(
            key_frame,
            text="👁️",
            width=40,
            height=30,
            fg_color=("#3B8ED0", "#1F6AA5"),
            text_color="white",
            border_width=0,
            command=self.toggle_key_visibility,
        )
        self.btn_show_hide.pack(side="left", padx=(0, 20))

        btn_save_key = ctk.CTkButton(
            key_frame,
            text="Enregistrer la clé",
            width=150,
            command=self.save_current_key,
        )
        btn_save_key.pack(anchor="e", padx=20, pady=(10, 15))

        # Test connection button
        btn_test = ctk.CTkButton(
            key_frame,
            text="Tester la connexion",
            width=150,
            fg_color=("#FF9800", "#F57C00"),
            hover_color=("#FB8C00", "#E65100"),
            command=self.test_connection,
        )
        btn_test.pack(anchor="e", padx=20, pady=(0, 15))

        # Logs Section
        logs_frame = ctk.CTkFrame(self.detail_panel, fg_color=("gray95", "gray20"))
        logs_frame.pack(fill="both", expand=True, pady=(10, 10))
        
        ctk.CTkLabel(
            logs_frame,
            text="📋 Logs de Connexion",
            font=("Arial", 12, "bold"),
        ).pack(anchor="w", padx=15, pady=(10, 5))

        self.log_textbox = ctk.CTkTextbox(
            logs_frame,
            height=150,
            font=("Consolas", 10),
            fg_color=("white", "gray25"),
            text_color=("gray20", "gray90"),
            wrap="word",
        )
        self.log_textbox.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        self.log_textbox.insert("1.0", "Aucun test effectué pour le moment.\nCliquez sur 'Tester la connexion' pour vérifier votre clé API.")
        self.log_textbox.configure(state="disabled")

        # Activation Section
        if self.selected_provider != self.active_provider:
            action_frame = ctk.CTkFrame(self.detail_panel, fg_color="transparent")
            action_frame.pack(fill="x", pady=30)
            lbl_info = ctk.CTkLabel(
                action_frame,
                text="Voulez-vous utiliser ce modèle pour tous vos assistants ?",
                text_color="gray",
            )
            lbl_info.pack(anchor="w", pady=(0, 10))
            btn_activate = ctk.CTkButton(
                action_frame,
                text="Définir comme Modèle par Défaut",
                fg_color="#4CAF50",
                hover_color="#388E3C",
                height=40,
                font=("Arial", 12, "bold"),
                command=self.set_as_active,
            )
            btn_activate.pack(fill="x")

    def add_log(self, message, status="info"):
        """Add a log entry to the log textbox with timestamp and icon."""
        if not self.log_textbox:
            return
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Icons based on status
        icons = {
            "success": "✅",
            "error": "❌",
            "info": "ℹ️",
            "warning": "⚠️"
        }
        icon = icons.get(status, "ℹ️")
        
        log_entry = f"[{timestamp}] {icon} {message}\n"
        
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")  # Clear previous logs
        self.log_textbox.insert("1.0", log_entry)
        self.log_textbox.configure(state="disabled")

    def toggle_key_visibility(self):
        if self.entry_key.cget("show") == "*":
            self.entry_key.configure(show="")
            self.btn_show_hide.configure(text="🔒")
        else:
            self.entry_key.configure(show="*")
            self.btn_show_hide.configure(text="👁️")

    def save_current_key(self):
        new_key = self.entry_key.get().strip()
        self.api_keys[self.selected_provider] = new_key
        try:
            self.app.data_manager.save_configuration(self.active_provider, self.api_keys)
            messagebox.showinfo("Succès", f"Clé API pour {self.selected_provider} enregistrée.")
            self.add_log(f"Clé API enregistrée pour {self.selected_provider}", "success")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde : {e}")
            self.add_log(f"Erreur sauvegarde: {str(e)}", "error")

    def set_as_active(self):
        # Save key first if changed
        current_input_key = self.entry_key.get().strip()
        if current_input_key != self.api_keys.get(self.selected_provider, ""):
            self.api_keys[self.selected_provider] = current_input_key
        self.active_provider = self.selected_provider
        try:
            self.app.data_manager.save_configuration(self.active_provider, self.api_keys)
            self.refresh_sidebar()
            self.refresh_detail_panel()
            messagebox.showinfo("Succès", f"{self.active_provider} est maintenant le modèle par défaut.")
            self.add_log(f"{self.active_provider} défini comme modèle par défaut", "success")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'activation : {e}")
            self.add_log(f"Erreur activation: {str(e)}", "error")

    def test_connection(self):
        """
        Test de connexion au LLM provider sélectionné.
        Utilise automatiquement le bon code de connexion selon le provider.
        """
        api_key = self.entry_key.get().strip()
        
        # Vérification de la présence de la clé API
        if not api_key:
            self.add_log(f"Aucune clé API saisie pour {self.selected_provider}", "error")
            messagebox.showerror("Erreur", f"Aucune clé API saisie pour {self.selected_provider}.")
            return
        
        # Log de début de test
        self.add_log(f"Test de connexion en cours pour {self.selected_provider}...", "info")
        
        # Test de connexion via le module LLMConnectionTester
        success, message = LLMConnectionTester.test_provider(self.selected_provider, api_key)
        
        if success:
            # Connexion réussie
            self.add_log(message, "success")
            messagebox.showinfo("Succès", f"✅ Connexion réussie à {self.selected_provider}.\n\nLa clé API est valide !")
        else:
            # Connexion échouée - Analyse de l'erreur pour donner une synthèse
            error_str = message
            
            # Synthèse des erreurs courantes
            if "authentication" in error_str.lower() or "api_key" in error_str.lower() or "401" in error_str:
                error_summary = "Clé API invalide ou expirée"
            elif "quota" in error_str.lower() or "429" in error_str:
                error_summary = "Quota dépassé ou limite de requêtes atteinte"
            elif "network" in error_str.lower() or "connection" in error_str.lower():
                error_summary = "Problème de connexion réseau"
            elif "model" in error_str.lower():
                error_summary = "Modèle non disponible ou non autorisé"
            elif "not found" in error_str.lower() or "404" in error_str:
                error_summary = "Ressource non trouvée"
            else:
                error_summary = "Erreur inconnue"
            
            # Afficher le message d'erreur COMPLET dans les logs
            error_msg = f"Échec: {error_summary}\n\nMessage d'erreur complet:\n{error_str}"
            self.add_log(error_msg, "error")
            messagebox.showerror("Erreur", f"❌ Échec de la connexion à {self.selected_provider}\n\n{error_summary}\n\nDétails:\n{error_str[:300]}")
