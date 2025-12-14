import customtkinter as ctk
from tkinter import messagebox

class AssistantDetailFrame(ctk.CTkFrame):
    def __init__(self, master, app, assistant_data):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.assistant = assistant_data
        
        # Header avec bouton retour
        header_frame = ctk.CTkFrame(self, fg_color="transparent", height=60)
        header_frame.pack(fill="x", padx=20, pady=10)
        header_frame.pack_propagate(False)
        
        btn_back = ctk.CTkButton(
            header_frame,
            text="< Retour",
            width=100,
            height=32,
            fg_color=("#3B8ED0", "#1F6AA5"),
            corner_radius=16,
            command=self.app.show_list,
        )
        btn_back.pack(side="left")
        
        title = ctk.CTkLabel(
            header_frame,
            text=f"Éditer : {self.assistant.get('name', 'Assistant')}",
            font=("Arial", 20, "bold")
        )
        title.pack(side="left", padx=20)
        
        # Bouton Sauvegarder
        btn_save = ctk.CTkButton(
            header_frame,
            text="💾 Sauvegarder",
            width=130,
            height=35,
            fg_color=("#4CAF50", "#388E3C"),
            hover_color=("#45A049", "#2E7D32"),
            corner_radius=18,
            font=("Arial", 13, "bold"),
            command=self.save_changes,
        )
        btn_save.pack(side="right")
        
        # Main scrollable frame pour les champs
        self.scrollable_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scrollable_frame.pack(fill="both", expand=True, padx=40, pady=(0, 20))
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        
        # Nom
        ctk.CTkLabel(
            self.scrollable_frame,
            text="📝 Nom de l'assistant *",
            font=("Arial", 14, "bold")
        ).grid(row=0, column=0, pady=(10, 5), sticky="w")
        
        self.entry_name = ctk.CTkEntry(
            self.scrollable_frame,
            height=40,
            font=("Arial", 12)
        )
        self.entry_name.insert(0, self.assistant.get("name", ""))
        self.entry_name.grid(row=1, column=0, pady=(0, 20), sticky="ew")
        
        # Description
        ctk.CTkLabel(
            self.scrollable_frame,
            text="💬 Description courte *",
            font=("Arial", 14, "bold")
        ).grid(row=2, column=0, pady=(0, 5), sticky="w")
        
        self.entry_desc = ctk.CTkEntry(
            self.scrollable_frame,
            height=40,
            font=("Arial", 12)
        )
        self.entry_desc.insert(0, self.assistant.get("description", ""))
        self.entry_desc.grid(row=3, column=0, pady=(0, 20), sticky="ew")
        
        # Rôle
        ctk.CTkLabel(
            self.scrollable_frame,
            text="🎭 Rôle",
            font=("Arial", 14, "bold")
        ).grid(row=4, column=0, pady=(0, 5), sticky="w")
        
        self.text_role = ctk.CTkTextbox(
            self.scrollable_frame,
            height=80,
            font=("Arial", 12),
            wrap="word"
        )
        self.text_role.insert("1.0", self.assistant.get("role", ""))
        self.text_role.grid(row=5, column=0, pady=(0, 20), sticky="ew")
        
        # Contexte
        ctk.CTkLabel(
            self.scrollable_frame,
            text="🌍 Contexte",
            font=("Arial", 14, "bold")
        ).grid(row=6, column=0, pady=(0, 5), sticky="w")
        
        self.text_context = ctk.CTkTextbox(
            self.scrollable_frame,
            height=80,
            font=("Arial", 12),
            wrap="word"
        )
        self.text_context.insert("1.0", self.assistant.get("context", ""))
        self.text_context.grid(row=7, column=0, pady=(0, 20), sticky="ew")
        
        # Objectif
        ctk.CTkLabel(
            self.scrollable_frame,
            text="🎯 Objectif",
            font=("Arial", 14, "bold")
        ).grid(row=8, column=0, pady=(0, 5), sticky="w")
        
        self.text_objective = ctk.CTkTextbox(
            self.scrollable_frame,
            height=80,
            font=("Arial", 12),
            wrap="word"
        )
        self.text_objective.insert("1.0", self.assistant.get("objective", ""))
        self.text_objective.grid(row=9, column=0, pady=(0, 20), sticky="ew")
        
        # Limites
        ctk.CTkLabel(
            self.scrollable_frame,
            text="⚠️ Limites",
            font=("Arial", 14, "bold")
        ).grid(row=10, column=0, pady=(0, 5), sticky="w")
        
        self.text_limits = ctk.CTkTextbox(
            self.scrollable_frame,
            height=80,
            font=("Arial", 12),
            wrap="word"
        )
        self.text_limits.insert("1.0", self.assistant.get("limits", ""))
        self.text_limits.grid(row=11, column=0, pady=(0, 20), sticky="ew")
        
        # Format de réponse
        ctk.CTkLabel(
            self.scrollable_frame,
            text="📋 Format de réponse",
            font=("Arial", 14, "bold")
        ).grid(row=12, column=0, pady=(0, 5), sticky="w")
        
        self.text_response_format = ctk.CTkTextbox(
            self.scrollable_frame,
            height=80,
            font=("Arial", 12),
            wrap="word"
        )
        self.text_response_format.insert("1.0", self.assistant.get("response_format", ""))
        self.text_response_format.grid(row=13, column=0, pady=(0, 20), sticky="ew")

        # URL Cible
        ctk.CTkLabel(
            self.scrollable_frame,
            text="🌐 URL Cible (pour recherche)",
            font=("Arial", 14, "bold")
        ).grid(row=14, column=0, pady=(0, 5), sticky="w")
        
        self.entry_url = ctk.CTkEntry(
            self.scrollable_frame,
            height=40,
            font=("Arial", 12)
        )
        self.entry_url.insert(0, self.assistant.get("target_url", ""))
        self.entry_url.grid(row=15, column=0, pady=(0, 20), sticky="ew")
        
        # Instructions URL (simplifié avec IA)
        ctk.CTkLabel(
            self.scrollable_frame,
            text="📝 Données à extraire (décrivez en français ce que vous voulez)",
            font=("Arial", 12),
            text_color="gray"
        ).grid(row=16, column=0, pady=(0, 5), sticky="w")
        
        self.text_url_instructions = ctk.CTkTextbox(
            self.scrollable_frame,
            height=100,
            font=("Arial", 12),
            wrap="word"
        )
        self.text_url_instructions.insert("1.0", self.assistant.get("url_instructions", ""))
        self.text_url_instructions.grid(row=17, column=0, pady=(0, 20), sticky="ew")
        
        # Provider
        ctk.CTkLabel(
            self.scrollable_frame,
            text="🤖 Provider LLM",
            font=("Arial", 14, "bold")
        ).grid(row=18, column=0, pady=(0, 5), sticky="w")
        
        settings = self.app.data_manager.get_settings()
        provider_list = list(settings.get("api_keys", {}).keys())
        if not provider_list:
            provider_list = [settings.get("current_provider", "OpenAI GPT-4o mini")]
        
        self.provider_var = ctk.StringVar(value=self.assistant.get("provider", provider_list[0]))
        self.provider_dropdown = ctk.CTkOptionMenu(
            self.scrollable_frame,
            values=provider_list,
            variable=self.provider_var,
            width=400
        )
        self.provider_dropdown.grid(row=19, column=0, pady=(0, 20), sticky="w")

        # Scraping Solution selection
        ctk.CTkLabel(
            self.scrollable_frame,
            text="🔧 Solution de Scraping",
            font=("Arial", 14, "bold")
        ).grid(row=20, column=0, pady=(0, 5), sticky="w")
        
        # Récupérer la solution par défaut depuis les settings
        default_solution = settings.get("scraping_solution", "scrapegraphai")
        current_solution = self.assistant.get("scraping_solution", default_solution)
        
        self.scraping_solution_var = ctk.StringVar(value=current_solution)
        scraping_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        scraping_frame.grid(row=21, column=0, pady=(0, 20), sticky="w")
        
        radio_scrapegraph = ctk.CTkRadioButton(
            scraping_frame,
            text="🤖 ScrapeGraphAI (IA - Payant)",
            variable=self.scraping_solution_var,
            value="scrapegraphai"
        )
        radio_scrapegraph.pack(side="left", padx=(0, 20))
        
        radio_playwright = ctk.CTkRadioButton(
            scraping_frame,
            text="🎭 Playwright (Gratuit)",
            variable=self.scraping_solution_var,
            value="playwright"
        )
        radio_playwright.pack(side="left")
    
    def save_changes(self):
        """Sauvegarde les modifications de l'assistant."""
        name = self.entry_name.get().strip()
        description = self.entry_desc.get().strip()
        role = self.text_role.get("1.0", "end-1c").strip()
        context = self.text_context.get("1.0", "end-1c").strip()
        objective = self.text_objective.get("1.0", "end-1c").strip()
        limits = self.text_limits.get("1.0", "end-1c").strip()
        response_format = self.text_response_format.get("1.0", "end-1c").strip()
        target_url = self.entry_url.get().strip()
        url_instructions = self.text_url_instructions.get("1.0", "end-1c").strip()
        provider = self.provider_var.get()
        scraping_solution = self.scraping_solution_var.get()
        
        # Validation
        if not name:
            messagebox.showerror("Erreur", "Le nom de l'assistant est obligatoire.")
            return
        
        if not description:
            messagebox.showerror("Erreur", "La description est obligatoire.")
            return
        
        # Mettre à jour l'assistant
        self.app.data_manager.update_assistant(
            assistant_id=self.assistant["id"],
            name=name,
            description=description,
            role=role,
            context=context,
            objective=objective,
            limits=limits,
            response_format=response_format,
            target_url=target_url,
            url_instructions=url_instructions,
            provider=provider,
            scraping_solution=scraping_solution
        )
        
        # Afficher un message de succès
        messagebox.showinfo("Succès", f"L'assistant '{name}' a été mis à jour avec succès !")
        
        # Retourner à la liste
        self.app.show_list()
