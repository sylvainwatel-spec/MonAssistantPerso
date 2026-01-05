import customtkinter as ctk
from tkinter import messagebox

class ListProfilesFrame(ctk.CTkFrame):
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
            text="Profils",
            font=("Arial", 24, "bold")
        )
        title.pack(side="left", padx=20)
        
        # Bouton pour créer un nouveau profil
        btn_new = ctk.CTkButton(
            header_frame,
            text="+ Nouveau Profil",
            width=150,
            height=35,
            fg_color=("#4CAF50", "#388E3C"),
            hover_color=("#45A049", "#2E7D32"),
            corner_radius=18,
            font=("Arial", 13, "bold"),
            command=self.app.show_profile_create,
        )
        btn_new.pack(side="right")
        
        # Frame scrollable pour les cartes de profils
        self.scrollable_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scrollable_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        
        # Charger et afficher les profils
        self.load_profiles()
    
    def load_profiles(self):
        """Charge et affiche tous les profils sous forme de cartes."""
        # Nettoyer le frame
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        profiles = self.app.data_manager.get_all_profiles()
        
        if not profiles:
            # Message si aucun profil
            empty_label = ctk.CTkLabel(
                self.scrollable_frame,
                text="Aucun profil créé pour le moment.\n\nCliquez sur '+ Nouveau Profil' pour commencer !",
                font=("Arial", 14),
                text_color="gray"
            )
            empty_label.grid(row=0, column=0, pady=100)
        else:
            # Créer une carte pour chaque profil
            for idx, profile in enumerate(profiles):
                self.create_profile_card(profile, idx)
    
    def create_profile_card(self, profile, row):
        """Crée une carte visuelle pour un profil."""
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
        
        # Icône de profil (gauche)
        icon_label = ctk.CTkLabel(
            card,
            text="👤",
            font=("Arial", 32),
            width=50
        )
        icon_label.grid(row=0, column=0, rowspan=3, padx=(15, 10), pady=15)
        
        # Informations du profil (centre)
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.grid(row=0, column=1, rowspan=3, sticky="ew", padx=(0, 10), pady=15)
        info_frame.grid_columnconfigure(0, weight=1)
        
        # Nom
        name_label = ctk.CTkLabel(
            info_frame,
            text=profile.get("name", "Sans nom"),
            font=("Arial", 16, "bold"),
            anchor="w"
        )
        name_label.grid(row=0, column=0, sticky="w")
        
        # Description
        desc_label = ctk.CTkLabel(
            info_frame,
            text=profile.get("description", "Aucune description"),
            font=("Arial", 12),
            text_color="gray",
            anchor="w"
        )
        desc_label.grid(row=1, column=0, sticky="w", pady=(5, 0))
        
        # Nombre d'assistants utilisant ce profil
        assistants = self.app.data_manager.get_all_assistants()
        usage_count = sum(1 for a in assistants if a.get("profile_id") == profile["id"] and a.get("use_profile"))
        
        usage_label = ctk.CTkLabel(
            info_frame,
            text=f"📊 Utilisé par {usage_count} assistant(s)",
            font=("Arial", 11),
            text_color=("gray50", "gray60"),
            anchor="w"
        )
        usage_label.grid(row=2, column=0, sticky="w", pady=(5, 0))
        
        # Boutons d'action (droite)
        actions_frame = ctk.CTkFrame(card, fg_color="transparent")
        actions_frame.grid(row=0, column=2, rowspan=3, padx=15, pady=15)
        
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
            command=lambda p=profile: self.edit_profile(p)
        )
        btn_edit.grid(row=0, column=0, padx=5)
        
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
            command=lambda p=profile: self.delete_profile(p)
        )
        btn_delete.grid(row=0, column=1, padx=5)
    
    def edit_profile(self, profile):
        """Ouvre la page de détail/édition du profil."""
        self.app.show_profile_detail(profile)
    
    def delete_profile(self, profile):
        """Supprime un profil après confirmation."""
        # Vérifier si le profil est utilisé
        assistants = self.app.data_manager.get_all_assistants()
        usage_count = sum(1 for a in assistants if a.get("profile_id") == profile["id"] and a.get("use_profile"))
        
        if usage_count > 0:
            result = messagebox.askyesno(
                "Confirmation",
                f"Ce profil est utilisé par {usage_count} assistant(s).\n\n"
                f"Si vous le supprimez, ces assistants conserveront leurs valeurs actuelles mais ne seront plus liés au profil.\n\n"
                f"Voulez-vous continuer ?",
                icon='warning'
            )
        else:
            result = messagebox.askyesno(
                "Confirmation",
                f"Êtes-vous sûr de vouloir supprimer le profil '{profile.get('name')}' ?\n\nCette action est irréversible.",
                icon='warning'
            )
        
        if result:
            # Détacher les assistants utilisant ce profil
            for assistant in assistants:
                if assistant.get("profile_id") == profile["id"] and assistant.get("use_profile"):
                    # Récupérer la config effective avant suppression
                    effective_config = self.app.data_manager.get_effective_assistant_config(assistant["id"])
                    # Mettre à jour l'assistant avec les valeurs effectives
                    self.app.data_manager.update_assistant(
                        assistant["id"],
                        role=effective_config.get("role", ""),
                        context=effective_config.get("context", ""),
                        objective=effective_config.get("objective", ""),
                        limits=effective_config.get("limits", ""),
                        response_format=effective_config.get("response_format", ""),
                        profile_id=None,
                        use_profile=False
                    )
            
            # Supprimer le profil
            self.app.data_manager.delete_profile(profile["id"])
            
            # Recharger la liste
            self.load_profiles()
            
            messagebox.showinfo("Succès", f"Le profil '{profile.get('name')}' a été supprimé.")
