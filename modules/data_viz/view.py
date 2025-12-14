import customtkinter as ctk

class DataVizFrame(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.build_ui()

    def build_ui(self):
        # Header
        header = ctk.CTkFrame(self, height=60, corner_radius=0)
        header.pack(fill="x", padx=20, pady=10)
        
        btn_back = ctk.CTkButton(
            header,
            text="< Accueil",
            width=100,
            height=32,
            fg_color=("gray70", "gray30"),
            corner_radius=16,
            command=self.app.show_home,
        )
        btn_back.pack(side="left", padx=10, pady=10)
        
        title = ctk.CTkLabel(header, text="📈 Data Visualization (Bientôt)", font=("Arial", 20, "bold"))
        title.pack(side="left", padx=20)

        # Content Placeholder
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            content, 
            text="Fonctionnalité en cours de développement.\nRevenez bientôt !",
            font=("Arial", 16),
            text_color="gray50"
        ).place(relx=0.5, rely=0.5, anchor="center")
