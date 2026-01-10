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

        current_row = 1

        # === SECTION 1: INFORMATIONS ESSENTIELLES ===
        
        # Nom
        ctk.CTkLabel(
            self.scrollable_frame,
            text="📝 Nom de l'assistant *",
            font=("Arial", 14, "bold")
        ).grid(row=current_row, column=0, pady=(0, 5), sticky="w")
        current_row += 1
        
        self.entry_name = ctk.CTkEntry(
            self.scrollable_frame,
            placeholder_text="Ex: Assistant Marketing Facebook",
            height=40,
            font=("Arial", 12)
        )
        self.entry_name.grid(row=current_row, column=0, pady=(0, 20), sticky="ew")
        current_row += 1

        # Description
        ctk.CTkLabel(
            self.scrollable_frame,
            text="💬 Description courte *",
            font=("Arial", 14, "bold")
        ).grid(row=current_row, column=0, pady=(0, 5), sticky="w")
        current_row += 1
        
        self.entry_desc = ctk.CTkEntry(
            self.scrollable_frame,
            placeholder_text="Ex: Spécialisé en publicité Facebook",
            height=40,
            font=("Arial", 12)
        )
        self.entry_desc.grid(row=current_row, column=0, pady=(0, 20), sticky="ew")
        current_row += 1

        # Profile selection
        ctk.CTkLabel(
            self.scrollable_frame,
            text="👤 Profil",
            font=("Arial", 14, "bold")
        ).grid(row=current_row, column=0, pady=(0, 5), sticky="w")
        current_row += 1
        
        # Récupérer les profils disponibles
        profiles = self.app.data_manager.get_all_profiles()
        profile_names = ["Aucun"] + [p["name"] for p in profiles]
        self.profile_map = {p["name"]: p for p in profiles}
        
        self.profile_var = ctk.StringVar(value="Aucun")
        self.profile_dropdown = ctk.CTkOptionMenu(
            self.scrollable_frame,
            values=profile_names,
            variable=self.profile_var,
            width=400,
            command=self.on_profile_selected
        )
        self.profile_dropdown.grid(row=current_row, column=0, pady=(0, 5), sticky="w")
        current_row += 1
        
        # Bouton "Créer un nouveau profil"
        btn_create_profile = ctk.CTkButton(
            self.scrollable_frame,
            text="+ Créer un nouveau profil",
            command=self.app.show_profile_create,
            fg_color="transparent",
            text_color=("#2196F3", "#42A5F5"),
            hover_color=("gray90", "gray25"),
            height=28,
            font=("Arial", 11)
        )
        btn_create_profile.grid(row=current_row, column=0, pady=(0, 5), sticky="w")
        current_row += 1
        
        # Info label
        self.profile_info_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="💡 Sélectionnez un profil ou créez-en un nouveau",
            font=("Arial", 10),
            text_color="gray"
        )
        self.profile_info_label.grid(row=current_row, column=0, pady=(0, 20), sticky="w")
        current_row += 1

        # === SECTION 2: CONFIGURATION TECHNIQUE ===

        # Provider selection
        settings = self.app.data_manager.get_settings()
        api_keys = settings.get("api_keys", {})
        
        # Liste officielle des providers (tel que défini dans l'admin)
        OFFICIAL_PROVIDERS = [
            "OpenAI",
            "Google Gemini",
            "Anthropic Claude",
            "Groq",
            "Mistral AI",
            "Hugging Face",
            "DeepSeek",
            "IAKA (Interne)"
        ]
        
        # Filtrer : Doit être officiel ET avoir une clé configurée
        provider_list = [p for p in OFFICIAL_PROVIDERS if p in api_keys and api_keys[p] and api_keys[p].strip()]
        
        # Fallback if no provider configured
        if not provider_list:
            provider_list = ["OpenAI (Défaut)"]
            
        default_provider = settings.get("current_provider", provider_list[0])
        if "IAKA (Interne)" in provider_list:
            default_provider = "IAKA (Interne)"
        elif default_provider not in provider_list:
            default_provider = provider_list[0]
        
        ctk.CTkLabel(
            self.scrollable_frame,
            text="🤖 Provider LLM",
            font=("Arial", 14, "bold")
        ).grid(row=current_row, column=0, pady=(0, 5), sticky="w")
        current_row += 1
        
        self.provider_var = ctk.StringVar(value=default_provider)
        self.provider_dropdown = ctk.CTkOptionMenu(
            self.scrollable_frame,
            values=provider_list,
            variable=self.provider_var,
            width=400
        )
        self.provider_dropdown.grid(row=current_row, column=0, pady=(0, 20), sticky="w")
        current_row += 1

        # Knowledge Base selection
        ctk.CTkLabel(
            self.scrollable_frame,
            text="📚 Base de Connaissances (RAG)",
            font=("Arial", 14, "bold")
        ).grid(row=current_row, column=0, pady=(0, 5), sticky="w")
        current_row += 1
        
        # Récupérer les KBs disponibles
        kbs = self.app.data_manager.get_all_knowledge_bases()
        kb_names = ["Aucune"] + [kb["name"] for kb in kbs]
        self.kb_map = {kb["name"]: kb["id"] for kb in kbs}
        
        # Trouver la KB actuelle si en mode édition? (Pour l'instant create only, mais on va assumer default)
        default_kb = "Aucune"
        # TODO: Si on ajoute le mode édition plus tard, il faudra charger la valeur ici
        
        self.kb_var = ctk.StringVar(value=default_kb)
        self.kb_dropdown = ctk.CTkOptionMenu(
            self.scrollable_frame,
            values=kb_names,
            variable=self.kb_var,
            width=400
        )
        self.kb_dropdown.grid(row=current_row, column=0, pady=(0, 20), sticky="w")
        current_row += 1

        # Scraping Solution selection
        ctk.CTkLabel(
            self.scrollable_frame,
            text="🔧 Solution de Scraping",
            font=("Arial", 14, "bold")
        ).grid(row=current_row, column=0, pady=(0, 5), sticky="w")
        current_row += 1
        
        default_solution = settings.get("scraping_solution", "scrapegraphai")
        
        self.scraping_solution_var = ctk.StringVar(value=default_solution)
        scraping_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        scraping_frame.grid(row=current_row, column=0, pady=(0, 20), sticky="w")
        current_row += 1
        
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

        # === SECTION 3: CONTEXTE DÉTAILLÉ (Masqué par défaut) ===
        
        self.context_section = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        self.context_section_row = current_row
        # Ne pas grid() ce frame pour l'instant, il sera affiché conditionnellement
        
        context_row = 0
        
        # Rôle
        ctk.CTkLabel(
            self.context_section,
            text="🎭 Rôle",
            font=("Arial", 14, "bold")
        ).grid(row=context_row, column=0, pady=(0, 5), sticky="w")
        context_row += 1
        
        self.text_role = ctk.CTkTextbox(
            self.context_section,
            height=80,
            font=("Arial", 12),
            wrap="word"
        )
        self.text_role.grid(row=context_row, column=0, pady=(0, 20), sticky="ew")
        context_row += 1

        # Contexte
        ctk.CTkLabel(
            self.context_section,
            text="🌍 Contexte",
            font=("Arial", 14, "bold")
        ).grid(row=context_row, column=0, pady=(0, 5), sticky="w")
        context_row += 1
        
        self.text_context = ctk.CTkTextbox(
            self.context_section,
            height=100,
            font=("Arial", 12),
            wrap="word"
        )
        self.text_context.grid(row=context_row, column=0, pady=(0, 20), sticky="ew")
        context_row += 1

        # Objectif
        ctk.CTkLabel(
            self.context_section,
            text="🎯 Objectif",
            font=("Arial", 14, "bold")
        ).grid(row=context_row, column=0, pady=(0, 5), sticky="w")
        context_row += 1
        
        self.text_objective = ctk.CTkTextbox(
            self.context_section,
            height=80,
            font=("Arial", 12),
            wrap="word"
        )
        self.text_objective.grid(row=context_row, column=0, pady=(0, 20), sticky="ew")
        context_row += 1

        # Limites
        ctk.CTkLabel(
            self.context_section,
            text="⚠️ Limites",
            font=("Arial", 14, "bold")
        ).grid(row=context_row, column=0, pady=(0, 5), sticky="w")
        context_row += 1
        
        self.text_limits = ctk.CTkTextbox(
            self.context_section,
            height=80,
            font=("Arial", 12),
            wrap="word"
        )
        self.text_limits.grid(row=context_row, column=0, pady=(0, 20), sticky="ew")
        context_row += 1

        # Format de réponse
        ctk.CTkLabel(
            self.context_section,
            text="📋 Format de réponse",
            font=("Arial", 14, "bold")
        ).grid(row=context_row, column=0, pady=(0, 5), sticky="w")
        context_row += 1
        
        self.text_response_format = ctk.CTkTextbox(
            self.context_section,
            height=80,
            font=("Arial", 12),
            wrap="word"
        )
        self.text_response_format.grid(row=context_row, column=0, pady=(0, 20), sticky="ew")
        context_row += 1
        
        # Afficher la section contexte par défaut (profil = "Aucun")
        self.context_section.grid(row=self.context_section_row, column=0, sticky="ew")
        current_row += 1

        # === SECTION 4: RECHERCHE WEB (Optionnel) ===

        # URL Analysis Section
        ctk.CTkLabel(
            self.scrollable_frame,
            text="🌐 URL à analyser (Optionnel)",
            font=("Arial", 14, "bold")
        ).grid(row=current_row, column=0, pady=(0, 5), sticky="w")
        current_row += 1

        self.url_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        self.url_frame.grid(row=current_row, column=0, pady=(0, 20), sticky="ew")
        self.url_frame.grid_columnconfigure(0, weight=1)
        current_row += 1

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

        # Instructions URL
        ctk.CTkLabel(
            self.scrollable_frame,
            text="📝 Données à extraire",
            font=("Arial", 12),
            text_color="gray"
        ).grid(row=current_row, column=0, pady=(5, 5), sticky="w")
        current_row += 1
        
        self.text_url_instructions = ctk.CTkTextbox(
            self.scrollable_frame,
            height=80,
            font=("Arial", 12),
            wrap="word"
        )
        self.text_url_instructions.grid(row=current_row, column=0, pady=(0, 20), sticky="ew")
        self.text_url_instructions.insert("1.0", "Décrivez simplement ce que vous voulez extraire, par exemple:\n\n\"Trouve les annonces avec le titre, le prix et la localisation\"")
        current_row += 1

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
        btn_save.grid(row=current_row, column=0, pady=(0, 20))

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
                
                # Mise à jour de l'UI - Ajouter au contexte si visible
                if self.context_section.winfo_ismapped():
                    self.text_context.insert("end", f"\n\n--- Contenu analysé ---\n{text_content}")
                messagebox.showinfo("Succès", "Analyse terminée ! Le contenu a été ajouté au contexte.")
            else:
                messagebox.showerror("Erreur", "Impossible de récupérer le contenu de la page.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue : {e}")
        finally:
            self.btn_analyze.configure(state="normal", text="🔍 Analyser")

    def on_profile_selected(self, selected_name):
        """Affiche/masque les champs de contexte selon le profil sélectionné."""
        if selected_name == "Aucun":
            # Afficher la section contexte
            self.context_section.grid(row=self.context_section_row, column=0, sticky="ew")
            self.profile_info_label.configure(text="💡 Remplissez les champs de contexte ci-dessous")
        else:
            # Masquer la section contexte
            self.context_section.grid_forget()
            profile = self.profile_map.get(selected_name)
            if profile:
                self.profile_info_label.configure(text=f"✅ Contexte défini par le profil : {selected_name}")
                
                # Pré-remplir les champs masqués pour la sauvegarde
                self.text_role.delete("1.0", "end")
                self.text_role.insert("1.0", profile.get("role", ""))
                
                self.text_context.delete("1.0", "end")
                self.text_context.insert("1.0", profile.get("context", ""))
                
                self.text_objective.delete("1.0", "end")
                self.text_objective.insert("1.0", profile.get("objective", ""))
                
                self.text_limits.delete("1.0", "end")
                self.text_limits.insert("1.0", profile.get("limits", ""))
                
                self.text_response_format.delete("1.0", "end")
                self.text_response_format.insert("1.0", profile.get("response_format", ""))

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
        scraping_solution = self.scraping_solution_var.get()
        
        # Knowledge Base ID logic
        kb_name = self.kb_var.get()
        knowledge_base_id = self.kb_map.get(kb_name) if kb_name != "Aucune" else None

        # Validation
        if not name:
            messagebox.showerror("Erreur", "Le nom de l'assistant est obligatoire.")
            return
        
        if not description:
            messagebox.showerror("Erreur", "La description est obligatoire.")
            return

        # Déterminer le profil sélectionné
        selected_profile_name = self.profile_var.get()
        profile_id = None
        use_profile = False
        
        if selected_profile_name != "Aucun":
            profile = self.profile_map.get(selected_profile_name)
            if profile:
                profile_id = profile["id"]
                use_profile = True

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
            provider=provider,
            scraping_solution=scraping_solution,
            profile_id=profile_id,
            use_profile=use_profile,
            knowledge_base_id=knowledge_base_id
        )

        # Mettre à jour le provider actif
        settings = self.app.data_manager.get_settings()
        settings["current_provider"] = provider
        self.app.data_manager.save_configuration(
            chat_provider=provider,
            scrapegraph_provider=settings.get("scrapegraph_provider", ""),
            api_keys=settings.get("api_keys", {}),
            endpoints=settings.get("endpoints", {})
        )

        # Afficher un message de succès
        messagebox.showinfo("Succès", f"L'assistant '{name}' a été créé avec succès !")

        # Retourner à la liste
        self.app.show_list()
