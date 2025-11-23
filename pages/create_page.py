import customtkinter as ctk
from tkinter import messagebox

class CreateAssistantFrame(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        
        # Header with back button
        btn_back = ctk.CTkButton(
            self,
            text="< Accueil",
            width=100,
            height=32,
            fg_color=("#3B8ED0", "#1F6AA5"),
            corner_radius=16,
            command=self.app.show_home,
        )
        btn_back.place(x=20, y=20)

        # Main scrollable frame pour contenir tous les champs
        self.scrollable_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scrollable_frame.pack(fill="both", expand=True, padx=40, pady=(80, 20))
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        # Title
        title = ctk.CTkLabel(
            self.scrollable_frame,
            text="Créer un Nouvel Assistant",
            font=("Arial", 24, "bold")
        )
        title.grid(row=0, column=0, pady=(0, 30), sticky="w")

        # Provider selection
        settings = self.app.data_manager.get_settings()
        provider_list = list(settings.get("api_keys", {}).keys())
        if not provider_list:
            provider_list = [settings.get("current_provider", "OpenAI GPT-4o mini")]
        
        ctk.CTkLabel(
            self.scrollable_frame,
            text="🤖 Provider LLM",
            font=("Arial", 14, "bold")
        ).grid(row=1, column=0, pady=(0, 5), sticky="w")
        
        self.provider_var = ctk.StringVar(value=settings.get("current_provider", provider_list[0]))
        self.provider_dropdown = ctk.CTkOptionMenu(
            self.scrollable_frame,
            values=provider_list,
            variable=self.provider_var,
            width=400
        )
        self.provider_dropdown.grid(row=2, column=0, pady=(0, 20), sticky="w")

        # Nom
        ctk.CTkLabel(
            self.scrollable_frame,
            text="📝 Nom de l'assistant *",
            font=("Arial", 14, "bold")
        ).grid(row=3, column=0, pady=(0, 5), sticky="w")
        
        self.entry_name = ctk.CTkEntry(
            self.scrollable_frame,
            placeholder_text="Ex: Assistant Marketing",
            height=40,
            font=("Arial", 12)
        )
        self.entry_name.grid(row=4, column=0, pady=(0, 20), sticky="ew")

        # Description
        ctk.CTkLabel(
            self.scrollable_frame,
            text="💬 Description courte *",
            font=("Arial", 14, "bold")
        ).grid(row=5, column=0, pady=(0, 5), sticky="w")
        
        self.entry_desc = ctk.CTkEntry(
            self.scrollable_frame,
            placeholder_text="Ex: Spécialisé en stratégie marketing digital",
            height=40,
            font=("Arial", 12)
        )
        self.entry_desc.grid(row=6, column=0, pady=(0, 20), sticky="ew")

        # Rôle
        ctk.CTkLabel(
            self.scrollable_frame,
            text="🎭 Rôle",
            font=("Arial", 14, "bold")
        ).grid(row=7, column=0, pady=(0, 5), sticky="w")
        
        self.text_role = ctk.CTkTextbox(
            self.scrollable_frame,
            height=80,
            font=("Arial", 12),
            wrap="word"
        )
        self.text_role.grid(row=8, column=0, pady=(0, 20), sticky="ew")
        self.text_role.insert("1.0", "Ex: Expert en marketing digital avec 10 ans d'expérience...")

        # Contexte
        ctk.CTkLabel(
            self.scrollable_frame,
            text="🌍 Contexte",
            font=("Arial", 14, "bold")
        ).grid(row=9, column=0, pady=(0, 5), sticky="w")
        
        self.text_context = ctk.CTkTextbox(
            self.scrollable_frame,
            height=80,
            font=("Arial", 12),
            wrap="word"
        )
        self.text_context.grid(row=10, column=0, pady=(0, 20), sticky="ew")
        self.text_context.insert("1.0", "Ex: Vous travaillez pour une agence de marketing digital...")

        # Objectif
        ctk.CTkLabel(
            self.scrollable_frame,
            text="🎯 Objectif",
            font=("Arial", 14, "bold")
        ).grid(row=11, column=0, pady=(0, 5), sticky="w")
        
        self.text_objective = ctk.CTkTextbox(
            self.scrollable_frame,
            height=80,
            font=("Arial", 12),
            wrap="word"
        )
        self.text_objective.grid(row=12, column=0, pady=(0, 20), sticky="ew")
        self.text_objective.insert("1.0", "Ex: Aider à créer des campagnes marketing efficaces...")

        # Limites
        ctk.CTkLabel(
            self.scrollable_frame,
            text="⚠️ Limites",
            font=("Arial", 14, "bold")
        ).grid(row=13, column=0, pady=(0, 5), sticky="w")
        
        self.text_limits = ctk.CTkTextbox(
            self.scrollable_frame,
            height=80,
            font=("Arial", 12),
            wrap="word"
        )
        self.text_limits.grid(row=14, column=0, pady=(0, 20), sticky="ew")
        self.text_limits.insert("1.0", "Ex: Ne pas donner de conseils financiers ou juridiques...")

        # Format de réponse
        ctk.CTkLabel(
            self.scrollable_frame,
            text="📋 Format de réponse",
            font=("Arial", 14, "bold")
        ).grid(row=15, column=0, pady=(0, 5), sticky="w")
        
        self.text_response_format = ctk.CTkTextbox(
            self.scrollable_frame,
            height=80,
            font=("Arial", 12),
            wrap="word"
        )
        self.text_response_format.grid(row=16, column=0, pady=(0, 30), sticky="ew")
        self.text_response_format.insert("1.0", "Ex: Réponses structurées avec bullet points et exemples concrets...")

        # Bouton de création
        btn_save = ctk.CTkButton(
            self.scrollable_frame,
            text="✨ Créer l'Assistant",
            width=300,
            height=50,
            corner_radius=25,
            font=("Arial", 16, "bold"),
            fg_color=("#4CAF50", "#388E3C"),
            hover_color=("#45A049", "#2E7D32"),
            command=self.save,
        )
        btn_save.grid(row=17, column=0, pady=(0, 20))

    def save(self):
        """Sauvegarde l'assistant avec tous les champs."""
        name = self.entry_name.get().strip()
        description = self.entry_desc.get().strip()
        role = self.text_role.get("1.0", "end-1c").strip()
        context = self.text_context.get("1.0", "end-1c").strip()
        objective = self.text_objective.get("1.0", "end-1c").strip()
        limits = self.text_limits.get("1.0", "end-1c").strip()
        response_format = self.text_response_format.get("1.0", "end-1c").strip()
        provider = self.provider_var.get()

        # Validation
        if not name:
            messagebox.showerror("Erreur", "Le nom de l'assistant est obligatoire.")
            return
        
        if not description:
            messagebox.showerror("Erreur", "La description est obligatoire.")
            return

        # Sauvegarder l'assistant
        self.app.data_manager.save_assistant(
            name=name,
            description=description,
            role=role,
            context=context,
            objective=objective,
            limits=limits,
            response_format=response_format,
            provider=provider
        )

        # Mettre à jour le provider actif
        settings = self.app.data_manager.get_settings()
        settings["current_provider"] = provider
        self.app.data_manager.save_configuration(settings["current_provider"], settings.get("api_keys", {}))

        # Afficher un message de succès
        messagebox.showinfo("Succès", f"L'assistant '{name}' a été créé avec succès !")

        # Retourner à la liste
        self.app.show_list()
