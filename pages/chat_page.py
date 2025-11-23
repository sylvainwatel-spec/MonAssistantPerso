import customtkinter as ctk
from tkinter import messagebox
from utils.llm_connector import LLMConnectionTester
import threading

class ChatFrame(ctk.CTkFrame):
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
            text=f"💬 Chat avec {self.assistant.get('name', 'Assistant')}",
            font=("Arial", 20, "bold")
        )
        title.pack(side="left", padx=20)
        
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
        
        # Message de bienvenue
        self.add_system_message(f"Bienvenue ! Vous discutez avec {self.assistant.get('name')}.")
        if self.assistant.get('description'):
            self.add_system_message(f"Description : {self.assistant.get('description')}")
        
        # Zone d'input
        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.pack(fill="x", padx=20, pady=(0, 20))
        input_frame.grid_columnconfigure(0, weight=1)
        
        self.entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Tapez votre message...",
            height=50,
            font=("Arial", 13)
        )
        self.entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.entry.bind("<Return>", lambda e: self.send_message())
        
        self.btn_send = ctk.CTkButton(
            input_frame,
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
    
    def add_system_message(self, text):
        """Ajoute un message système."""
        self.chat_area.configure(state="normal")
        self.chat_area.insert("end", f"ℹ️ {text}\n\n", "system")
        self.chat_area.tag_config("system", foreground="gray")
        self.chat_area.configure(state="disabled")
        self.chat_area.see("end")
    
    def add_user_message(self, text):
        """Ajoute un message de l'utilisateur."""
        self.chat_area.configure(state="normal")
        self.chat_area.insert("end", f"Vous : {text}\n\n", "user")
        self.chat_area.tag_config("user", foreground="#2196F3")
        self.chat_area.configure(state="disabled")
        self.chat_area.see("end")
    
    def add_assistant_message(self, text):
        """Ajoute un message de l'assistant."""
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
        
        return "\n\n".join(parts) if parts else "Tu es un assistant utile et serviable."
    
    def send_message(self):
        """Envoie un message au LLM."""
        user_message = self.entry.get().strip()
        
        if not user_message:
            return
        
        # Afficher le message de l'utilisateur
        self.add_user_message(user_message)
        self.entry.delete(0, "end")
        
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
            else:
                response_text = f"Provider {provider} non supporté pour le moment."
            
            # Afficher la réponse
            self.add_assistant_message(response_text)
            
        except Exception as e:
            self.add_error_message(str(e))
        
        finally:
            # Réactiver le bouton d'envoi
            self.btn_send.configure(state="normal", text="Envoyer")
    
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
            model="llama3-8b-8192",
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
