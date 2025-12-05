import customtkinter as ctk

class ToolTip:
    """Classe pour créer des tooltips au survol."""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.after_id = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)
    
    def show_tooltip(self, event=None):
        # Utiliser les coordonnées du widget directement
        x = self.widget.winfo_rootx() + self.widget.winfo_width() // 2
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        
        # Créer le tooltip seulement s'il n'existe pas déjà
        if self.tooltip is None:
            self.tooltip = ctk.CTkToplevel(self.widget)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{x}+{y}")
            
            # Ajouter un binding pour fermer si on perd le focus
            self.tooltip.bind("<FocusOut>", self.hide_tooltip)
            
            label = ctk.CTkLabel(
                self.tooltip,
                text=self.text,
                font=("Arial", 11),
                fg_color=("gray90", "gray20"),
                corner_radius=6,
                padx=10,
                pady=5
            )
            label.pack()
            
            # Auto-fermeture après 3 secondes
            self.after_id = self.widget.after(3000, self.hide_tooltip)
    
    def hide_tooltip(self, event=None):
        # Annuler le timer si il existe
        if self.after_id:
            try:
                self.widget.after_cancel(self.after_id)
            except:
                pass
            self.after_id = None
        
        # Détruire le tooltip
        if self.tooltip:
            try:
                self.tooltip.destroy()
            except:
                pass
            self.tooltip = None

class HomeFrame(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1) # Spacer top
        self.grid_rowconfigure(4, weight=1) # Spacer bottom

        # Admin Button (Top Right) - Amélioré
        if hasattr(self.app, 'settings_icon') and self.app.settings_icon:
            btn_admin = ctk.CTkButton(
                self,
                text="",
                image=self.app.settings_icon,
                width=60,
                height=60,
                fg_color=("gray85", "gray25"),
                hover_color=("gray75", "gray35"),
                corner_radius=30,
                command=self.app.show_admin
            )
        else:
            btn_admin = ctk.CTkButton(
                self,
                text="⚙️",
                width=60,
                height=60,
                font=("Arial", 24),
                fg_color=("gray85", "gray25"),
                hover_color=("gray75", "gray35"),
                corner_radius=30,
                command=self.app.show_admin
            )
        btn_admin.place(relx=0.95, rely=0.05, anchor="ne")
        
        # Ajouter le tooltip
        ToolTip(btn_admin, "Administration")

        # Avatar Central
        if hasattr(self.app, 'avatar_image') and self.app.avatar_image:
            label = ctk.CTkLabel(self, text="", image=self.app.avatar_image)
            label.grid(row=1, column=0, pady=(20, 10))
        
        welcome = ctk.CTkLabel(self, text="Bienvenue", font=ctk.CTkFont(size=32, weight="bold"))
        welcome.grid(row=2, column=0, pady=(0, 30))

        # Bouton Principal : Mes Assistants (centré)
        btn_list = ctk.CTkButton(
            self, 
            text="Mes Assistants", 
            font=ctk.CTkFont(size=18, weight="bold"),
            width=200, 
            height=60, 
            corner_radius=30,
            command=self.app.show_list
        )
        btn_list.grid(row=3, column=0, pady=20)
