import customtkinter as ctk
from tkinter import messagebox

class CreateAssistantFrame(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.grid_columnconfigure(0, weight=1)

        # Header avec retour
        btn_back = ctk.CTkButton(self, text="< Accueil", width=100, height=32, fg_color=("#3B8ED0", "#1F6AA5"), corner_radius=16,
                                 command=self.app.show_home)
        btn_back.place(x=20, y=20)

        title = ctk.CTkLabel(self, text="Nouvel Assistant", font=ctk.CTkFont(size=24, weight="bold"))
        title.grid(row=0, column=0, pady=(80, 40))

        self.entry_name = ctk.CTkEntry(self, placeholder_text="Nom de l'assistant", width=300, height=40)
        self.entry_name.grid(row=1, column=0, pady=10)

        self.entry_desc = ctk.CTkEntry(self, placeholder_text="Description courte", width=300, height=40)
        self.entry_desc.grid(row=2, column=0, pady=10)

        btn_save = ctk.CTkButton(self, text="Créer l'Assistant", width=200, height=50, corner_radius=25,
                                 font=ctk.CTkFont(size=16, weight="bold"),
                                 command=self.save)
        btn_save.grid(row=3, column=0, pady=40)

    def save(self):
        name = self.entry_name.get()
        desc = self.entry_desc.get()
        if name:
            self.app.data_manager.save_assistant(name, desc)
            self.app.show_list()
        else:
            messagebox.showerror("Erreur", "Le nom est obligatoire.")
