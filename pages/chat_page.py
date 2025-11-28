import customtkinter as ctk
from tkinter import messagebox, filedialog
from utils.llm_connector import LLMConnectionTester
from utils.web_scraper import WebScraper
import threading
import datetime
import os

class ChatFrame(ctk.CTkFrame):
    def __init__(self, master, app, assistant_data):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.assistant = assistant_data
        self.history = [] # Liste pour stocker l'historique des messages
        
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
            text=f"💬 Chat avec {self.assistant.get('name', 'Assistant')}",
            font=("Arial", 20, "bold")
        )
        title.pack(side="left", padx=20)
        
        # Bouton Export Excel
        btn_export = ctk.CTkButton(
            header_frame,
            text="📥 Export Excel",
            width=120,
            height=32,
            fg_color=("#2E7D32", "#1B5E20"), # Vert foncé
            corner_radius=16,
            command=self.export_to_excel
        )
        btn_export.pack(side="right", padx=10)
        
        # Indicateur de provider
        provider_label = ctk.CTkLabel(
            header_frame,
            text=f"🤖 {self.assistant.get('provider', 'Non défini')}",
            font=("Arial", 12),
            text_color="gray"
        )
        provider_label.pack(side="right", padx=10)
        
        # Zone de chat
        self.chat_area = ctk.CTkTextbox(
            self,
            font=("Arial", 13),
            wrap="word"
        )
        self.chat_area.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        self.chat_area.configure(state="disabled")
        
        # Barre de progression (cachée par défaut)
        self.progress_bar = ctk.CTkProgressBar(
            self,
            mode="indeterminate",
            height=8,
            corner_radius=4,
            progress_color=("#4CAF50", "#4CAF50"),
            fg_color=("gray85", "gray25")
        )
        self.progress_bar.set(0) # Initialiser à 0
        
        # Zone d'input
        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.pack(fill="x", padx=20, pady=(0, 20))
        self.input_frame.grid_columnconfigure(0, weight=1)
        
        self.entry = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="Tapez votre message...",
            height=50,
            font=("Arial", 13)
        )
        self.entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.entry.bind("<Return>", lambda e: self.send_message())
        
        self.btn_send = ctk.CTkButton(
            self.input_frame,
            text="Envoyer",
            width=100,
            height=50,
            corner_radius=25,
            fg_color=("#4CAF50", "#388E3C"),
            hover_color=("#45A049", "#2E7D32"),
            font=("Arial", 13, "bold"),
            command=self.send_message
        )
        self.btn_send.grid(row=0, column=1)
        
        # Message de bienvenue et envoi automatique
        self.add_system_message(f"Connexion à {self.assistant.get('name')}...")
        if self.assistant.get('description'):
            self.add_system_message(f"Description : {self.assistant.get('description')}")
        
        # Envoyer automatiquement un message de bienvenue au LLM
        self.after(500, self.send_welcome_message)
    
    
    def send_welcome_message(self):
        """Envoie automatiquement un message de bienvenue au LLM."""
        if self.assistant.get('target_url'):
            welcome_msg = "Bonjour ! Présente-toi brièvement et lance immédiatement la recherche sur le site cible en fonction de ton objectif. IMPORTANT : Respecte scrupuleusement les consignes définies dans tes instructions (Contexte, Objectif, Limites)."
        else:
            welcome_msg = "Bonjour ! Peux-tu te présenter brièvement ?"
            
        self.add_user_message(welcome_msg)
        
        # Afficher l'indicateur de chargement
        self.show_loading()
        
        # Désactiver le bouton d'envoi
        self.btn_send.configure(state="disabled", text="Envoi...")
        
        # Envoyer la requête au LLM dans un thread séparé
        thread = threading.Thread(target=self._send_to_llm, args=(welcome_msg,))
        thread.daemon = True
        thread.start()
    
    def show_loading(self):
        """Affiche l'indicateur de chargement."""
        self.progress_bar.pack(fill="x", padx=20, pady=(0, 10), before=self.input_frame)
        self.progress_bar.start()
    
    def hide_loading(self):
        """Cache l'indicateur de chargement."""
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
    
    def add_system_message(self, text):
        """Ajoute un message système."""
        self.history.append({"role": "Système", "content": text, "timestamp": datetime.datetime.now()})
        self.chat_area.configure(state="normal")
        self.chat_area.insert("end", f"ℹ️ {text}\n\n", "system")
        self.chat_area.tag_config("system", foreground="gray")
        self.chat_area.configure(state="disabled")
        self.chat_area.see("end")
    
    def add_user_message(self, text):
        """Ajoute un message de l'utilisateur."""
        self.history.append({"role": "Utilisateur", "content": text, "timestamp": datetime.datetime.now()})
        self.chat_area.configure(state="normal")
        self.chat_area.insert("end", f"Vous : {text}\n\n", "user")
        self.chat_area.tag_config("user", foreground="#2196F3")
        self.chat_area.configure(state="disabled")
        self.chat_area.see("end")
    
    def add_assistant_message(self, text):
        """Ajoute un message de l'assistant."""
        self.history.append({"role": "Assistant", "content": text, "timestamp": datetime.datetime.now()})
        self.chat_area.configure(state="normal")
        self.chat_area.insert("end", f"{self.assistant.get('name')} : {text}\n\n", "assistant")
        self.chat_area.tag_config("assistant", foreground="#4CAF50")
        self.chat_area.configure(state="disabled")
        self.chat_area.see("end")
    
    def add_error_message(self, text):
        """Ajoute un message d'erreur."""
        self.chat_area.configure(state="normal")
        self.chat_area.insert("end", f"❌ Erreur : {text}\n\n", "error")
        self.chat_area.tag_config("error", foreground="#F44336")
        self.chat_area.configure(state="disabled")
        self.chat_area.see("end")
    
    def build_system_prompt(self):
        """Construit le prompt système avec toutes les informations de l'assistant."""
        parts = []
        
        if self.assistant.get('role'):
            parts.append(f"Rôle : {self.assistant.get('role')}")
        
        if self.assistant.get('context'):
            parts.append(f"Contexte : {self.assistant.get('context')}")
        
        if self.assistant.get('objective'):
            parts.append(f"Objectif : {self.assistant.get('objective')}")
        
        if self.assistant.get('limits'):
            parts.append(f"Limites : {self.assistant.get('limits')}")
        
        if self.assistant.get('response_format'):
            parts.append(f"Format de réponse : {self.assistant.get('response_format')}")
            
        # Instructions pour l'outil de recherche
        target_url = self.assistant.get('target_url')
        if target_url:
            parts.append(f"""
IMPORTANT : Tu as accès à un outil de recherche sur le site : {target_url}
Pour effectuer une recherche sur ce site, réponds UNIQUEMENT avec la commande suivante :
ACTION: SEARCH <ta requête de recherche>

Exemple :
Utilisateur : "Cherche des chaussures rouges"
Toi : ACTION: SEARCH chaussures rouges

Je t'enverrai ensuite les résultats de la recherche, et tu pourras formuler ta réponse finale.
N'utilise cette commande que si c'est pertinent pour répondre à l'utilisateur.
""")
            
            # Instructions détaillées pour le site
            url_instructions = self.assistant.get('url_instructions')
            if url_instructions:
                parts.append(f"""
INSTRUCTIONS POUR LE SITE {target_url} :
Ces instructions sont automatiquement utilisées par le système de recherche pour :
- Localiser le champ de recherche correct
- Exécuter des actions préliminaires (ex: accepter les cookies)
- Extraire les résultats de manière structurée

Tu n'as pas besoin d'interpréter les commandes techniques (SEARCH_INPUT, etc.) manuellement car elles sont gérées par le système.
Cependant, si les instructions contiennent du texte explicatif ou des conseils de navigation, utilise-les pour mieux comprendre le contexte du site.
Concentre-toi sur la formulation de requêtes de recherche pertinentes et l'analyse des résultats retournés.
""")

        
        # Consignes de priorité
        parts.append("""
IMPORTANT :
1. Tu dois analyser et comprendre le fonctionnement du site internet cible pour naviguer et extraire les informations pertinentes.
2. MAIS SURTOUT : Ta PRIORITÉ ABSOLUE est de respecter scrupuleusement les consignes définies ci-dessus (Rôle, Contexte, Objectif, Limites).
3. En cas de conflit entre une information du site et tes instructions, tes instructions (Limites notamment) prévalent toujours.
""")

        return "\n\n".join(parts) if parts else "Tu es un assistant utile et serviable."
    
    def send_message(self):
        """Envoie un message au LLM."""
        user_message = self.entry.get().strip()
        
        if not user_message:
            return
        
        # Afficher le message de l'utilisateur
        self.add_user_message(user_message)
        self.entry.delete(0, "end")
        
        # Afficher l'indicateur de chargement
        self.show_loading()
        
        # Désactiver le bouton d'envoi
        self.btn_send.configure(state="disabled", text="Envoi...")
        
        # Envoyer la requête au LLM dans un thread séparé
        thread = threading.Thread(target=self._send_to_llm, args=(user_message,))
        thread.daemon = True
        thread.start()
    
    def _send_to_llm(self, user_message):
        """Envoie la requête au LLM (dans un thread séparé)."""
        try:
            # Récupérer la clé API
            settings = self.app.data_manager.get_settings()
            provider = self.assistant.get('provider', 'OpenAI GPT-4o mini')
            api_key = settings.get('api_keys', {}).get(provider)
            
            if not api_key:
                self.add_error_message(f"Aucune clé API configurée pour {provider}. Veuillez configurer votre clé dans la page Administration.")
                self.btn_send.configure(state="normal", text="Envoyer")
                return
            
            # Construire le prompt système
            system_prompt = self.build_system_prompt()
            
            # Appeler le LLM selon le provider
            # Appeler le LLM selon le provider
            if "OpenAI" in provider:
                response_text = self._call_openai(api_key, system_prompt, user_message)
            elif "Gemini" in provider:
                response_text = self._call_gemini(api_key, system_prompt, user_message)
            elif "Claude" in provider:
                response_text = self._call_claude(api_key, system_prompt, user_message)
            elif "Llama" in provider or "Groq" in provider:
                response_text = self._call_groq(api_key, system_prompt, user_message)
            elif "Mistral" in provider:
                response_text = self._call_mistral(api_key, system_prompt, user_message)
            elif "DeepSeek" in provider:
                 # DeepSeek utilise l'API OpenAI avec une base_url spécifique
                 response_text = self._call_openai_compatible(api_key, "https://api.deepseek.com", system_prompt, user_message)
            elif "IAKA" in provider:
                endpoint = settings.get('endpoints', {}).get(provider)
                if not endpoint:
                    raise Exception(f"Endpoint URL non configuré pour {provider}.")
                response_text = self._call_openai_compatible(api_key, endpoint, system_prompt, user_message)
            else:
                response_text = f"Provider {provider} non supporté pour le moment."
            
            # Traiter la réponse (vérifier si action requise)
            self._process_llm_response(response_text, api_key, system_prompt, user_message)
            
        except Exception as e:
            self.add_error_message(str(e))
        
        finally:
            # Cacher l'indicateur de chargement
            self.hide_loading()
            
            # Réactiver le bouton d'envoi
            self.btn_send.configure(state="normal", text="Envoyer")

    def _process_llm_response(self, response_text, api_key, system_prompt, original_user_message):
        """Traite la réponse du LLM et gère les actions (outils)."""
        
        # Vérifier si le LLM demande une action de recherche
        if "ACTION: SEARCH" in response_text:
            # Séparer le message de la commande
            parts = response_text.split("ACTION: SEARCH")
            intro_text = parts[0].strip()
            query = parts[1].strip()
            
            # Afficher le message d'intro s'il y en a un
            if intro_text:
                self.add_assistant_message(intro_text)
            
            self.add_system_message(f"🔎 Recherche en cours sur {self.assistant.get('target_url')} : '{query}'...")
            
            # Parser et afficher les instructions avant exécution
            url_instructions = self.assistant.get('url_instructions', '')
            scraper = WebScraper()
            
            if url_instructions:
                # Parser les instructions pour les afficher
                from utils.instruction_parser import InstructionParser
                parser = InstructionParser()
                try:
                    parsed = parser.parse(url_instructions)
                    is_valid, errors = parser.validate(parsed)
                    
                    if is_valid and parsed:
                        # Afficher les instructions parsées
                        instructions_summary = "📋 Instructions détectées et qui seront appliquées :\n"
                        
                        if 'search_input' in parsed:
                            instructions_summary += f"  ✓ Champ de recherche : {parsed['search_input']}\n"
                        else:
                            instructions_summary += f"  ⚙️ Champ de recherche : détection automatique\n"
                        
                        if 'search_button' in parsed:
                            instructions_summary += f"  ✓ Bouton de recherche : {parsed['search_button']}\n"
                        
                        if 'before_search' in parsed and parsed['before_search']:
                            instructions_summary += f"  ✓ Actions préliminaires :\n"
                            for action in parsed['before_search']:
                                if action['type'] == 'click':
                                    instructions_summary += f"    - Cliquer sur : {action['selector']}\n"
                                elif action['type'] == 'wait':
                                    instructions_summary += f"    - Attendre : {action['duration']}ms\n"
                                elif action['type'] == 'type':
                                    instructions_summary += f"    - Taper '{action['text']}' dans : {action['selector']}\n"
                        
                        if 'wait_for' in parsed:
                            instructions_summary += f"  ✓ Attendre l'élément : {parsed['wait_for']}\n"
                        
                        if 'results' in parsed:
                            instructions_summary += f"  ✓ Sélecteur de résultats : {parsed['results']}\n"
                        
                        if 'extract' in parsed and parsed['extract']:
                            instructions_summary += f"  ✓ Extraction structurée :\n"
                            for field, selector in parsed['extract'].items():
                                instructions_summary += f"    - {field} : {selector}\n"
                        
                        self.add_system_message(instructions_summary.strip())
                    elif errors:
                        self.add_system_message(f"⚠️ Instructions invalides (utilisation de la détection automatique) : {', '.join(errors)}")
                    else:
                        # Pas d'instructions structurées trouvées, mais du texte est présent
                        self.add_system_message(f"ℹ️ Instructions textuelles (non structurées) détectées :\n{url_instructions}\n\n⚙️ Le système utilisera la détection automatique pour la recherche, mais ces notes peuvent aider à comprendre le contexte.")
                except Exception as e:
                    self.add_system_message(f"⚠️ Erreur lors du parsing des instructions : {e}\n⚙️ Utilisation de la détection automatique")
            else:
                self.add_system_message("⚙️ Aucune instruction configurée, utilisation de la détection automatique")
            
            # Exécuter la recherche avec les instructions URL
            search_results = scraper.perform_search(
                self.assistant.get('target_url'), 
                query,
                instructions=url_instructions if url_instructions else None
            )
            
            # Limiter la taille des résultats
            if len(search_results) > 4000:
                search_results = search_results[:4000] + "... (tronqué)"
            
            # Relancer le LLM avec les résultats
            new_user_message = f"{original_user_message}\n\n[RÉSULTATS DE LA RECHERCHE pour '{query}']:\n{search_results}\n\nUtilise ces informations pour répondre à la demande initiale."
            
            # Appel récursif (attention à la boucle infinie, on pourrait ajouter un compteur)
            # Pour simplifier ici, on refait juste un appel standard
            if "OpenAI" in self.assistant.get('provider', ''):
                final_response = self._call_openai(api_key, system_prompt, new_user_message)
            elif "Gemini" in self.assistant.get('provider', ''):
                final_response = self._call_gemini(api_key, system_prompt, new_user_message)
            elif "Claude" in self.assistant.get('provider', ''):
                final_response = self._call_claude(api_key, system_prompt, new_user_message)
            elif "Llama" in self.assistant.get('provider', '') or "Groq" in self.assistant.get('provider', ''):
                final_response = self._call_groq(api_key, system_prompt, new_user_message)
            elif "Mistral" in self.assistant.get('provider', ''):
                final_response = self._call_mistral(api_key, system_prompt, new_user_message)
            elif "DeepSeek" in self.assistant.get('provider', ''):
                 final_response = self._call_openai_compatible(api_key, "https://api.deepseek.com", system_prompt, new_user_message)
            elif "IAKA" in self.assistant.get('provider', ''):
                settings = self.app.data_manager.get_settings()
                endpoint = settings.get('endpoints', {}).get(self.assistant.get('provider', ''))
                final_response = self._call_openai_compatible(api_key, endpoint, system_prompt, new_user_message)
            else:
                final_response = "Erreur: Provider non supporté pour la suite de l'action."
                
            self.add_assistant_message(final_response)
        else:
            # Réponse normale
            self.add_assistant_message(response_text)
    
    def _call_openai(self, api_key, system_prompt, user_message):
        """Appelle l'API OpenAI."""
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    
    def _call_openai_compatible(self, api_key, base_url, system_prompt, user_message):
        """Appelle une API compatible OpenAI (ex: IAKA)."""
        from openai import OpenAI
        client = OpenAI(api_key=api_key, base_url=base_url)
        
        # Essayer de déterminer le modèle à utiliser
        # Pour IAKA, on peut essayer un modèle par défaut ou lister
        try:
            # On tente d'abord avec un nom générique
            model_to_use = "gpt-3.5-turbo"
            
            # Si on peut lister les modèles, on prend le premier
            try:
                models = client.models.list()
                if models.data:
                    model_to_use = models.data[0].id
            except:
                pass
                
            response = client.chat.completions.create(
                model=model_to_use,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Erreur lors de l'appel à l'API compatible : {str(e)}"

    def _call_gemini(self, api_key, system_prompt, user_message):
        """Appelle l'API Google Gemini."""
        import google.generativeai as genai
        
        genai.configure(api_key=api_key)
        
        # Trouver un modèle disponible
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                model_name = m.name.lower()
                if 'preview' not in model_name and 'exp' not in model_name:
                    available_models.append(m.name)
        
        if not available_models:
            raise Exception("Aucun modèle Gemini disponible")
        
        # Prioriser flash
        flash_models = [m for m in available_models if 'flash' in m.lower()]
        model_name = flash_models[0] if flash_models else available_models[0]
        
        model = genai.GenerativeModel(model_name)
        
        # Combiner system prompt et user message
        full_prompt = f"{system_prompt}\n\nUtilisateur : {user_message}"
        
        response = model.generate_content(full_prompt)
        return response.text
    
    def _call_claude(self, api_key, system_prompt, user_message):
        """Appelle l'API Anthropic Claude."""
        from anthropic import Anthropic
        
        client = Anthropic(api_key=api_key)
        
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=500,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )
        
        return response.content[0].text
    
    def _call_groq(self, api_key, system_prompt, user_message):
        """Appelle l'API Groq (Llama)."""
        from groq import Groq
        
        client = Groq(api_key=api_key)
        
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    
    def _call_mistral(self, api_key, system_prompt, user_message):
        """Appelle l'API Mistral."""
        from mistralai.client import MistralClient
        
        client = MistralClient(api_key=api_key)
        
        # Combiner system prompt et user message
        full_message = f"{system_prompt}\n\nUtilisateur : {user_message}"
        
        response = client.chat(
            model="mistral-small-latest",
            messages=[
                {"role": "user", "content": full_message}
            ],
            max_tokens=500
        )
        
        return response.choices[0].message.content

    def export_to_excel(self):
        """Exporte le tableau de la 'Partie 2 : Synthèse à exporter' vers Excel."""
        if not self.history:
            messagebox.showinfo("Info", "Aucun message à exporter.")
            return
            
        # Rechercher la "Partie 2" dans les messages de l'assistant
        target_section = "Partie 2 : Synthèse à exporter"
        table_data = None
        
        # Parcourir l'historique à l'envers pour trouver le dernier message pertinent
        for msg in reversed(self.history):
            if msg["role"] == "Assistant" and target_section in msg["content"]:
                # Extraire le contenu après le titre de la section
                content = msg["content"]
                start_index = content.find(target_section) + len(target_section)
                section_content = content[start_index:]
                
                # Chercher un tableau Markdown
                table_data = self._parse_markdown_table(section_content)
                if table_data:
                    break
        
        if not table_data:
            messagebox.showwarning("Attention", f"Aucune table trouvée dans la section '{target_section}'.\nAssurez-vous que l'assistant a généré cette section avec un tableau.")
            return

        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
            
            # Demander l'emplacement de sauvegarde
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                initialfile=f"synthese_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                title="Exporter la synthèse"
            )
            
            if not filename:
                return
            
            # Créer le classeur Excel
            wb = Workbook()
            ws = wb.active
            ws.title = "Synthèse"
            
            # Styles
            header_fill = PatternFill(start_color="4CAF50", end_color="4CAF50", fill_type="solid")
            header_font = Font(bold=True, color="FFFFFF")
            center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
            thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
            
            # Écrire les en-têtes
            if table_data["headers"]:
                ws.append(table_data["headers"])
                for col_idx, cell in enumerate(ws[1], 1):
                    cell.fill = header_fill
                    cell.font = header_font
                    cell.alignment = center_align
                    cell.border = thin_border
            
            # Écrire les données
            for row in table_data["rows"]:
                ws.append(row)
                # Appliquer les bordures et l'alignement à la dernière ligne ajoutée
                for cell in ws[ws.max_row]:
                    cell.border = thin_border
                    cell.alignment = Alignment(vertical="center", wrap_text=True)
            
            # Ajuster la largeur des colonnes
            for col in ws.columns:
                max_length = 0
                column = col[0].column_letter # Get the column name
                for cell in col:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = (max_length + 2)
                # Limiter la largeur max pour éviter des colonnes géantes
                ws.column_dimensions[column].width = min(adjusted_width, 50)
            
            # Sauvegarder
            wb.save(filename)
            messagebox.showinfo("Succès", f"Synthèse exportée avec succès vers :\n{filename}")
            
        except ImportError:
            messagebox.showerror("Erreur", "Le module 'openpyxl' est manquant. Veuillez l'installer.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue lors de l'export :\n{str(e)}")

    def _parse_markdown_table(self, text):
        """Parse un tableau Markdown dans le texte donné."""
        lines = text.strip().split('\n')
        headers = []
        rows = []
        in_table = False
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Détection du début de tableau (ligne avec des |)
            if "|" in line:
                # Nettoyer la ligne (enlever les | de début et fin si présents)
                parts = [p.strip() for p in line.split('|') if p.strip()]
                
                if not parts:
                    continue
                    
                if not in_table:
                    # Potentiellement les en-têtes
                    # Vérifier si la ligne suivante est une ligne de séparation (---)
                    if i + 1 < len(lines) and "---" in lines[i+1]:
                        headers = parts
                        in_table = True
                        # Sauter la ligne de séparation
                        continue
                elif "---" in line:
                    # Ligne de séparation, on ignore
                    continue
                else:
                    # Ligne de données
                    rows.append(parts)
            elif in_table and not line:
                # Fin du tableau si ligne vide
                break
        
        if headers or rows:
            return {"headers": headers, "rows": rows}
        return None
