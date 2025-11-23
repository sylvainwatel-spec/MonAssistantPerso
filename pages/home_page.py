import customtkinter as ctk

class HomeFrame(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1) # Spacer top
        self.grid_rowconfigure(4, weight=1) # Spacer bottom

        # Admin Button (Top Right)
        if hasattr(self.app, 'settings_icon') and self.app.settings_icon:
            btn_admin = ctk.CTkButton(self, text="", image=self.app.settings_icon, width=40, height=40, 
                                      fg_color="transparent", hover_color=("gray70", "gray30"),
                                      command=self.app.show_admin)
        else:
            btn_admin = ctk.CTkButton(self, text="⚙️", width=40, height=40, 
                                      fg_color="transparent", hover_color=("gray70", "gray30"),
                                      command=self.app.show_admin)
        btn_admin.place(relx=0.95, rely=0.05, anchor="ne")

        # Avatar Central
        if hasattr(self.app, 'avatar_image') and self.app.avatar_image:
            label = ctk.CTkLabel(self, text="", image=self.app.avatar_image)
            label.grid(row=1, column=0, pady=(20, 10))
        
        welcome = ctk.CTkLabel(self, text="Bonjour, Maître.", font=ctk.CTkFont(size=32, weight="bold"))
        welcome.grid(row=2, column=0, pady=(0, 30))

        # Dock d'Actions
        dock_frame = ctk.CTkFrame(self, fg_color="transparent")
        dock_frame.grid(row=3, column=0, pady=20)

        # Bouton Principal : Mes Assistants
        btn_list = ctk.CTkButton(dock_frame, text="Mes Assistants", font=ctk.CTkFont(size=18, weight="bold"),
                                 width=200, height=60, corner_radius=30,
                                 command=self.app.show_list)
        btn_list.grid(row=0, column=0, padx=20)

        # Bouton Secondaire : Créer
        btn_create = ctk.CTkButton(dock_frame, text="+ Créer", font=ctk.CTkFont(size=16),
                                   width=120, height=50, corner_radius=25, fg_color=("#3B8ED0", "#1F6AA5"), border_width=0,
                                   command=self.app.show_create)
        btn_create.grid(row=0, column=1, padx=20)
