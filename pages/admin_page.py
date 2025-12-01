import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime

class AdminFrame(ctk.CTkFrame):
    """Page d'administration centrale - Sélection des LLM par défaut."""
    
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app

        # --- Data Loading ---
        try:
            self.settings = self.app.data_manager.get_settings()
        except Exception as e:
            print(f"Error loading settings: {e}")
            self.settings = {
                "chat_provider": "OpenAI GPT-4o mini",
                "scrapegraph_provider": "OpenAI GPT-4o mini",
                "api_keys": {},
                "endpoints": {}
            }
        
        self.chat_provider = self.settings.get("chat_provider", "OpenAI GPT-4o mini")
        self.scrapegraph_provider = self.settings.get("scrapegraph_provider", "OpenAI GPT-4o mini")
        self.api_keys = self.settings.get("api_keys", {})

        # --- Layout ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        self.create_header()

        # Main content
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=40, pady=20)
        self.content_frame.grid_columnconfigure(0, weight=1)

        self.create_content()

    def create_header(self):
        header = ctk.CTkFrame(self, height=60, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=10)

        btn_back = ctk.CTkButton(
            header,
            text="< Accueil",
            width=100,
            height=32,
            fg_color=("gray70", "gray30"),
            corner_radius=16,
            command=self.app.show_home,
        )
        btn_back.pack(side="left", padx=10)

        title = ctk.CTkLabel(header, text="⚙️ Administration & Modèles", font=("Arial", 24, "bold"))
        title.pack(side="left", padx=20)

    def create_content(self):
        # Title
        title_label = ctk.CTkLabel(
            self.content_frame,
            text="Configuration des Modèles LLM",
            font=("Arial", 18, "bold")
        )
        title_label.grid(row=0, column=0, sticky="w", pady=(0, 20))

        # Description
        desc_label = ctk.CTkLabel(
            self.content_frame,
            text="Configurez les modèles LLM par défaut pour le chat et pour ScrapeGraphAI.\nChaque connecteur peut utiliser un modèle différent.",
            font=("Arial", 12),
            text_color="gray",
            justify="left"
        )
        desc_label.grid(row=1, column=0, sticky="w", pady=(0, 30))

        # Chat LLM Section
        self.create_chat_section()

        # Separator
        separator = ctk.CTkFrame(self.content_frame, height=2, fg_color=("gray80", "gray30"))
        separator.grid(row=3, column=0, sticky="ew", pady=30)

        # ScrapeGraphAI LLM Section
        self.create_scrapegraph_section()

        # Separator
        separator2 = ctk.CTkFrame(self.content_frame, height=2, fg_color=("gray80", "gray30"))
        separator2.grid(row=5, column=0, sticky="ew", pady=30)

        # System Information Section
        self.create_system_info_section()

    def create_chat_section(self):
        """Section pour le LLM de chat."""
        chat_frame = ctk.CTkFrame(self.content_frame, fg_color=("gray95", "gray20"), corner_radius=12)
        chat_frame.grid(row=2, column=0, sticky="ew", pady=10)
        chat_frame.grid_columnconfigure(1, weight=1)

        # Icon and title
        icon_label = ctk.CTkLabel(chat_frame, text="💬", font=("Arial", 32))
        icon_label.grid(row=0, column=0, rowspan=2, padx=20, pady=20)

        title_label = ctk.CTkLabel(
            chat_frame,
            text="LLM par Défaut pour le Chat",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=1, sticky="w", pady=(20, 5))

        # Current provider info
        provider_info = ctk.CTkLabel(
            chat_frame,
            text=f"Modèle actuel : {self.chat_provider}",
            font=("Arial", 13),
            text_color=("gray30", "gray70")
        )
        provider_info.grid(row=1, column=1, sticky="w", pady=(0, 20))

        # Configure button
        btn_configure = ctk.CTkButton(
            chat_frame,
            text="Configurer le Connecteur Chat",
            width=220,
            height=40,
            fg_color=("#3B8ED0", "#1F6AA5"),
            hover_color=("#36719F", "#144870"),
            font=("Arial", 12, "bold"),
            command=self.app.show_chat_connector
        )
        btn_configure.grid(row=0, column=2, rowspan=2, padx=20, pady=20)

        # API Key status indicator
        has_key = self.chat_provider in self.api_keys and self.api_keys[self.chat_provider]
        status_color = "#4CAF50" if has_key else "#FF9800"
        status_text = "✓ Clé API configurée" if has_key else "⚠ Clé API manquante"
        
        status_label = ctk.CTkLabel(
            chat_frame,
            text=status_text,
            font=("Arial", 10),
            text_color=status_color
        )
        status_label.grid(row=2, column=1, sticky="w", pady=(0, 15), padx=(0, 0))

    def create_scrapegraph_section(self):
        """Section pour le LLM de ScrapeGraphAI."""
        sg_frame = ctk.CTkFrame(self.content_frame, fg_color=("gray95", "gray20"), corner_radius=12)
        sg_frame.grid(row=4, column=0, sticky="ew", pady=10)
        sg_frame.grid_columnconfigure(1, weight=1)

        # Icon and title
        icon_label = ctk.CTkLabel(sg_frame, text="🤖", font=("Arial", 32))
        icon_label.grid(row=0, column=0, rowspan=2, padx=20, pady=20)

        title_label = ctk.CTkLabel(
            sg_frame,
            text="LLM par Défaut pour ScrapeGraphAI",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=1, sticky="w", pady=(20, 5))

        # Current provider info
        provider_info = ctk.CTkLabel(
            sg_frame,
            text=f"Modèle actuel : {self.scrapegraph_provider}",
            font=("Arial", 13),
            text_color=("gray30", "gray70")
        )
        provider_info.grid(row=1, column=1, sticky="w", pady=(0, 20))

        # Configure button
        btn_configure = ctk.CTkButton(
            sg_frame,
            text="Configurer le Connecteur ScrapeGraphAI",
            width=260,
            height=40,
            fg_color=("#3B8ED0", "#1F6AA5"),
            hover_color=("#36719F", "#144870"),
            font=("Arial", 12, "bold"),
            command=self.app.show_scrapegraph_connector
        )
        btn_configure.grid(row=0, column=2, rowspan=2, padx=20, pady=20)

        # API Key status indicator
        has_key = self.scrapegraph_provider in self.api_keys and self.api_keys[self.scrapegraph_provider]
        status_color = "#4CAF50" if has_key else "#FF9800"
        status_text = "✓ Clé API configurée" if has_key else "⚠ Clé API manquante"
        
        status_label = ctk.CTkLabel(
            sg_frame,
            text=status_text,
            font=("Arial", 10),
            text_color=status_color
        )
        status_label.grid(row=2, column=1, sticky="w", pady=(0, 15), padx=(0, 0))

        # Compatibility note
        compatible_llms = ["OpenAI GPT-4o mini", "Google Gemini 1.5 Flash", "Meta Llama 3 (via Groq)"]
        is_compatible = self.scrapegraph_provider in compatible_llms
        
        if not is_compatible:
            compat_label = ctk.CTkLabel(
                sg_frame,
                text="⚠ Ce modèle n'est pas compatible avec ScrapeGraphAI",
                font=("Arial", 10),
                text_color="#FF5722"
            )
            compat_label.grid(row=3, column=1, sticky="w", pady=(0, 15))

    def create_system_info_section(self):
        """Section d'informations système."""
        info_frame = ctk.CTkFrame(self.content_frame, fg_color=("gray95", "gray20"), corner_radius=12)
        info_frame.grid(row=6, column=0, sticky="ew", pady=10)

        title_label = ctk.CTkLabel(
            info_frame,
            text="📊 Informations Système",
            font=("Arial", 16, "bold")
        )
        title_label.pack(anchor="w", padx=20, pady=(15, 10))

        # Count assistants
        try:
            assistants = self.app.data_manager.get_all_assistants()
            num_assistants = len(assistants)
        except:
            num_assistants = 0

        # Count configured LLMs (with API keys)
        num_configured_llms = len([k for k, v in self.api_keys.items() if v])

        # Info grid
        info_grid = ctk.CTkFrame(info_frame, fg_color="transparent")
        info_grid.pack(fill="x", padx=20, pady=(0, 15))
        info_grid.grid_columnconfigure((0, 1, 2), weight=1)

        # Assistants count
        assist_frame = ctk.CTkFrame(info_grid, fg_color=("gray90", "gray25"), corner_radius=8)
        assist_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        ctk.CTkLabel(
            assist_frame,
            text=str(num_assistants),
            font=("Arial", 24, "bold"),
            text_color=("#3B8ED0", "#1F6AA5")
        ).pack(pady=(10, 0))
        ctk.CTkLabel(
            assist_frame,
            text="Assistants créés",
            font=("Arial", 11),
            text_color="gray"
        ).pack(pady=(0, 10))

        # Configured LLMs count
        llm_frame = ctk.CTkFrame(info_grid, fg_color=("gray90", "gray25"), corner_radius=8)
        llm_frame.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        ctk.CTkLabel(
            llm_frame,
            text=str(num_configured_llms),
            font=("Arial", 24, "bold"),
            text_color=("#4CAF50", "#388E3C")
        ).pack(pady=(10, 0))
        ctk.CTkLabel(
            llm_frame,
            text="LLM configurés",
            font=("Arial", 11),
            text_color="gray"
        ).pack(pady=(0, 10))

        # Last modified (if available)
        try:
            import os
            settings_path = self.app.data_manager.settings_path
            if os.path.exists(settings_path):
                mtime = os.path.getmtime(settings_path)
                last_modified = datetime.fromtimestamp(mtime).strftime("%d/%m/%Y %H:%M")
            else:
                last_modified = "N/A"
        except:
            last_modified = "N/A"

        modified_frame = ctk.CTkFrame(info_grid, fg_color=("gray90", "gray25"), corner_radius=8)
        modified_frame.grid(row=0, column=2, sticky="ew", padx=5, pady=5)
        ctk.CTkLabel(
            modified_frame,
            text=last_modified,
            font=("Arial", 12, "bold"),
            text_color=("#FF9800", "#F57C00")
        ).pack(pady=(10, 0))
        ctk.CTkLabel(
            modified_frame,
            text="Dernière modification",
            font=("Arial", 11),
            text_color="gray"
        ).pack(pady=(0, 10))
