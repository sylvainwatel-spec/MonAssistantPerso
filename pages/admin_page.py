import customtkinter as ctk
from tkinter import messagebox

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

        # --- Layout ---
        self.grid_columnconfigure(1, weight=1) # Right panel expands
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
        
        btn_back = ctk.CTkButton(header, text="< Accueil", width=100, height=32, fg_color=("#3B8ED0", "#1F6AA5"), corner_radius=16,
                                 command=self.app.show_home)
        btn_back.pack(side="left", padx=10)
        
        title = ctk.CTkLabel(header, text="Administration & Modèles", font=("Arial", 20, "bold"))

    def refresh_sidebar(self):
        # Clear existing widgets safely
        for widget in self.sidebar_widgets:
            try:
                widget.destroy()
            except:
                pass
        self.sidebar_widgets = []

        lbl = ctk.CTkLabel(self.sidebar, text="Modèles Disponibles", font=("Arial", 14, "bold"), text_color="gray60")
        lbl.pack(pady=(10, 5), padx=10, anchor="w")
        self.sidebar_widgets.append(lbl)

        for provider in self.llm_options:
            self.create_sidebar_item(provider)

    def create_sidebar_item(self, provider):
        is_active = (provider == self.active_provider)
        is_selected = (provider == self.selected_provider)
        
        # Style
        btn_color = ("gray80", "gray25") if is_selected else "transparent"
        
        item_frame = ctk.CTkFrame(self.sidebar, fg_color=btn_color, corner_radius=6)
        item_frame.pack(fill="x", padx=5, pady=2)
        self.sidebar_widgets.append(item_frame)
        
        # Click event
        item_frame.bind("<Button-1>", lambda e, p=provider: self.select_provider(p))
        
        # Layout
        item_frame.grid_columnconfigure(1, weight=1)
        
        # Active Indicator
        indicator_text = "●" if is_active else ""
        indicator_color = "#4CAF50"
        indicator = ctk.CTkLabel(item_frame, text=indicator_text, text_color=indicator_color, font=("Arial", 16))
        indicator.grid(row=0, column=0, padx=(10, 5), pady=10)
        indicator.bind("<Button-1>", lambda e, p=provider: self.select_provider(p))

        # Name
        # name_font = ctk.CTkFont(size=13, weight="bold" if is_active else "normal")
        font_weight = "bold" if is_active else "normal"
        lbl_name = ctk.CTkLabel(item_frame, text=provider, font=("Arial", 13, font_weight))
        lbl_name.grid(row=0, column=1, sticky="w", padx=5)
        lbl_name.bind("<Button-1>", lambda e, p=provider: self.select_provider(p))
        
        # Active Badge
        if is_active:
            lbl_status = ctk.CTkLabel(item_frame, text="ACTIF", font=("Arial", 10, "bold"), text_color="#4CAF50")
            lbl_status.grid(row=0, column=2, padx=10)
            lbl_status.bind("<Button-1>", lambda e, p=provider: self.select_provider(p))

    def select_provider(self, provider):
        self.selected_provider = provider
        self.refresh_sidebar()
        self.refresh_detail_panel()

    def refresh_detail_panel(self):
        # Clear existing
        for widget in self.detail_panel.winfo_children():
            widget.destroy()
            
        if not self.selected_provider:
            return

        # Header
        ctk.CTkLabel(self.detail_panel, text=self.selected_provider, font=("Arial", 24, "bold")).pack(anchor="w", pady=(0, 5))
        
        if self.selected_provider == self.active_provider:
            ctk.CTkLabel(self.detail_panel, text="✅ Ce modèle est actuellement utilisé par défaut.", text_color="#4CAF50").pack(anchor="w", pady=(0, 20))
        else:
            ctk.CTkLabel(self.detail_panel, text="Ce modèle n'est pas actif.", text_color="gray").pack(anchor="w", pady=(0, 20))

        # API Key Section
        key_frame = ctk.CTkFrame(self.detail_panel)
        key_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(key_frame, text="Clé API", font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(15, 5))
        
        current_key = self.api_keys.get(self.selected_provider, "")
        self.entry_key = ctk.CTkEntry(key_frame, width=400, show="*")
        self.entry_key.insert(0, current_key)
        self.entry_key.pack(padx=20, pady=5, fill="x")
        
        btn_save_key = ctk.CTkButton(key_frame, text="Enregistrer la clé", width=150, 
                                     command=self.save_current_key)
        btn_save_key.pack(anchor="e", padx=20, pady=(10, 15))

        # Activation Section
        if self.selected_provider != self.active_provider:
            action_frame = ctk.CTkFrame(self.detail_panel, fg_color="transparent")
            action_frame.pack(fill="x", pady=30)
            
            lbl_info = ctk.CTkLabel(action_frame, text="Voulez-vous utiliser ce modèle pour tous vos assistants ?", text_color="gray")
            lbl_info.pack(anchor="w", pady=(0, 10))
            
            btn_activate = ctk.CTkButton(action_frame, text="Définir comme Modèle par Défaut", 
                                         fg_color="#4CAF50", hover_color="#388E3C", height=40,
                                         font=("Arial", 12, "bold"),
                                         command=self.set_as_active)
            btn_activate.pack(fill="x")

    def save_current_key(self):
        new_key = self.entry_key.get().strip()
        self.api_keys[self.selected_provider] = new_key
        
        try:
            self.app.data_manager.save_configuration(self.active_provider, self.api_keys)
            messagebox.showinfo("Succès", f"Clé API pour {self.selected_provider} enregistrée.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde : {e}")

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
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'activation : {e}")
