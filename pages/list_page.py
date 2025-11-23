import customtkinter as ctk
from tkinter import messagebox

class ListAssistantsFrame(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        
        # Header avec bouton retour
        header_frame = ctk.CTkFrame(self, fg_color="transparent", height=60)
        header_frame.pack(fill="x", padx=20, pady=10)
        header_frame.pack_propagate(False)
        
        btn_back = ctk.CTkButton(
            header_frame,
            text="< Accueil",
            width=100,
            height=32,
            fg_color=("#3B8ED0", "#1F6AA5"),
            corner_radius=16,
            command=self.app.show_home,
        )
        btn_back.pack(side="left")
        
        title = ctk.CTkLabel(
            header_frame,
            text="Mes Assistants",
            font=("Arial", 24, "bold")
        )
        title.pack(side="left", padx=20)
        
        # Bouton pour créer un nouvel assistant
        btn_new = ctk.CTkButton(
            header_frame,
            text="+ Nouvel Assistant",
            width=150,
            height=35,
            fg_color=("#4CAF50", "#388E3C"),
            hover_color=("#45A049", "#2E7D32"),
            corner_radius=18,
            font=("Arial", 13, "bold"),
            command=self.app.show_create,
        )
        btn_new.pack(side="right")
        
        # Frame scrollable pour les cartes d'assistants
        self.scrollable_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scrollable_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        
        # Charger et afficher les assistants
        self.load_assistants()
    
    def load_assistants(self):
        """Charge et affiche tous les assistants sous forme de cartes."""
        # Nettoyer le frame
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        assistants = self.app.data_manager.get_all_assistants()
        
        if not assistants:
            # Message si aucun assistant
            empty_label = ctk.CTkLabel(
                self.scrollable_frame,
                text="Aucun assistant créé pour le moment.\n\nCliquez sur '+ Nouvel Assistant' pour commencer !",
                font=("Arial", 14),
                text_color="gray"
            )
            empty_label.grid(row=0, column=0, pady=100)
        else:
            # Créer une carte pour chaque assistant
            for idx, assistant in enumerate(assistants):
                self.create_assistant_card(assistant, idx)
    
    def create_assistant_card(self, assistant, row):
        """Crée une carte visuelle pour un assistant."""
        # Frame principal de la carte
        card = ctk.CTkFrame(
            self.scrollable_frame,
            fg_color=("white", "gray20"),
            corner_radius=12,
            border_width=1,
            border_color=("gray80", "gray30")
        )
        card.grid(row=row, column=0, pady=10, sticky="ew", padx=5)
        card.grid_columnconfigure(1, weight=1)
        
        # Icône de statut (gauche)
        status_color = "#4CAF50" if assistant.get("status") == "running" else "#9E9E9E"
        status_text = "●"
        
        status_label = ctk.CTkLabel(
            card,
            text=status_text,
            font=("Arial", 24),
            text_color=status_color,
            width=40
        )
        status_label.grid(row=0, column=0, rowspan=3, padx=(15, 10), pady=15)
        
        # Informations de l'assistant (centre)
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.grid(row=0, column=1, rowspan=3, sticky="ew", padx=(0, 10), pady=15)
        info_frame.grid_columnconfigure(0, weight=1)
        
        # Nom
        name_label = ctk.CTkLabel(
            info_frame,
            text=assistant.get("name", "Sans nom"),
            font=("Arial", 16, "bold"),
            anchor="w"
        )
        name_label.grid(row=0, column=0, sticky="w")
        
        # Description
        desc_label = ctk.CTkLabel(
            info_frame,
            text=assistant.get("description", "Aucune description"),
            font=("Arial", 12),
            text_color="gray",
            anchor="w"
        )
        desc_label.grid(row=1, column=0, sticky="w", pady=(5, 0))
        
        # Provider
        provider = assistant.get("provider", "Non défini")
        provider_label = ctk.CTkLabel(
            info_frame,
            text=f"🤖 {provider}",
            font=("Arial", 11),
            text_color=("gray50", "gray60"),
            anchor="w"
        )
        provider_label.grid(row=2, column=0, sticky="w", pady=(5, 0))
        
        # Boutons d'action (droite)
        actions_frame = ctk.CTkFrame(card, fg_color="transparent")
        actions_frame.grid(row=0, column=2, rowspan=3, padx=15, pady=15)
        
        # Bouton Lancer (nouveau)
        btn_launch = ctk.CTkButton(
            actions_frame,
            text="▶",
            width=38,
            height=38,
            corner_radius=19,
            fg_color=("#4CAF50", "#388E3C"),
            hover_color=("#45A049", "#2E7D32"),
            font=("Arial", 16, "bold"),
            command=lambda a=assistant: self.launch_assistant(a)
        )
        btn_launch.grid(row=0, column=0, padx=5)
        
        # Bouton Modifier
        btn_edit = ctk.CTkButton(
            actions_frame,
            text="Modifier",
            width=90,
            height=38,
            corner_radius=19,
            fg_color=("#2196F3", "#1976D2"),
            hover_color=("#1E88E5", "#1565C0"),
            font=("Arial", 12, "bold"),
            command=lambda a=assistant: self.edit_assistant(a)
        )
        btn_edit.grid(row=0, column=1, padx=5)
        
        # Bouton Supprimer
        btn_delete = ctk.CTkButton(
            actions_frame,
            text="✕",
            width=38,
            height=38,
            corner_radius=19,
            fg_color=("white", "gray25"),
            hover_color=("#FFEBEE", "#B71C1C"),
            border_width=2,
            border_color=("#F44336", "#D32F2F"),
            text_color=("#F44336", "#D32F2F"),
            font=("Arial", 18, "bold"),
            command=lambda a=assistant: self.delete_assistant(a)
        )
        btn_delete.grid(row=0, column=2, padx=5)
    
    def launch_assistant(self, assistant):
        """Lance l'assistant et ouvre l'interface de chat."""
        self.app.show_chat(assistant)
    
    def edit_assistant(self, assistant):
        """Ouvre la page de détail/édition de l'assistant."""
        self.app.show_assistant_detail(assistant)
    
    def delete_assistant(self, assistant):
        """Supprime un assistant après confirmation."""
        result = messagebox.askyesno(
            "Confirmation",
            f"Êtes-vous sûr de vouloir supprimer l'assistant '{assistant.get('name')}' ?\n\nCette action est irréversible.",
            icon='warning'
        )
        
        if result:
            # Supprimer l'assistant
            assistants = self.app.data_manager.get_all_assistants()
            assistants = [a for a in assistants if a["id"] != assistant["id"]]
            self.app.data_manager._save_to_file(assistants)
            
            # Recharger la liste
            self.load_assistants()
            
            messagebox.showinfo("Succès", f"L'assistant '{assistant.get('name')}' a été supprimé.")
