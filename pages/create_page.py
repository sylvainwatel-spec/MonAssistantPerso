import customtkinter as ctk
from tkinter import messagebox
import threading
from utils.web_scraper import WebScraper

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
            height=120,
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

        # URL Analysis Section (Moved to bottom)
        ctk.CTkLabel(
            self.scrollable_frame,
            text="🌐 URL à analyser (Optionnel)",
            font=("Arial", 14, "bold")
        ).grid(row=17, column=0, pady=(0, 5), sticky="w")

        self.url_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        self.url_frame.grid(row=18, column=0, pady=(0, 20), sticky="ew")
        self.url_frame.grid_columnconfigure(0, weight=1)

        self.entry_url = ctk.CTkEntry(
            self.url_frame,
            placeholder_text="https://www.exemple.com",
            height=40,
            font=("Arial", 12)
        )
        self.entry_url.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        self.btn_analyze = ctk.CTkButton(
            self.url_frame,
            text="🔍 Analyser",
            width=100,
            height=40,
            fg_color=("#FF9800", "#F57C00"),
            hover_color=("#FB8C00", "#EF6C00"),
            command=self.analyze_url
        )
        self.btn_analyze.grid(row=0, column=1)

        # Instructions URL (simplifié avec IA)
        ctk.CTkLabel(
            self.scrollable_frame,
            text="📝 Données à extraire (décrivez en français ce que vous voulez)",
            font=("Arial", 12),
            text_color="gray"
        ).grid(row=19, column=0, pady=(5, 5), sticky="w")
        
        self.text_url_instructions = ctk.CTkTextbox(
            self.scrollable_frame,
            height=100,
            font=("Arial", 12),
            wrap="word"
        )
        self.text_url_instructions.grid(row=20, column=0, pady=(0, 20), sticky="ew")
        self.text_url_instructions.insert("1.0", """Décrivez simplement ce que vous voulez extraire, par exemple:

"Trouve les annonces avec le titre, le prix et la localisation"

ou

"Extrait les articles avec leur titre, auteur, date de publication et résumé"

L'IA comprendra automatiquement la structure de la page. Pas besoin de sélecteurs CSS !""")

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
        btn_save.grid(row=21, column=0, pady=(0, 20))

    def analyze_url(self):
        """Lance l'analyse de l'URL dans un thread séparé."""
        url = self.entry_url.get().strip()
        if not url:
            messagebox.showwarning("Attention", "Veuillez entrer une URL valide.")
            return
        
        self.btn_analyze.configure(state="disabled", text="Analyse...")
        threading.Thread(target=self._perform_analysis, args=(url,), daemon=True).start()

    def _perform_analysis(self, url):
        """Exécute le scraping et met à jour l'interface."""
        try:
            scraper = WebScraper()
            soup = scraper.fetch_page(url)
            
            if soup:
                text_content = scraper.extract_text(soup)
                # Limiter la taille du texte pour éviter de saturer le contexte
                max_chars = 5000
                if len(text_content) > max_chars:
                    text_content = text_content[:max_chars] + "\n... (Tronqué)"
                
                # Mise à jour de l'UI
                # On n'inclut plus l'URL dans le texte ajouté
                self.text_context.insert("end", f"\n\n--- Contenu analysé ---\n{text_content}")
                messagebox.showinfo("Succès", "Analyse terminée ! Le contenu a été ajouté au contexte.")
            else:
                messagebox.showerror("Erreur", "Impossible de récupérer le contenu de la page.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue : {e}")
        finally:
            self.btn_analyze.configure(state="normal", text="🔍 Analyser")

    def save(self):
        """Sauvegarde l'assistant avec tous les champs."""
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
            target_url=target_url,
            url_instructions=url_instructions,
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
