import customtkinter as ctk
from tkinter import messagebox

class ListAssistantsFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, app):
        super().__init__(master, label_text="", fg_color="transparent")
        self.app = app
        self.grid_columnconfigure((0, 1), weight=1) # 2 colonnes

        # Header custom hors du scrollable (astuce: on met le titre dans le parent si possible, mais ici on est le frame)
        # On va ajouter un bouton retour flottant
        btn_back = ctk.CTkButton(self, text="< Accueil", width=100, height=32, fg_color=("#3B8ED0", "#1F6AA5"), corner_radius=16,
                                 command=self.app.show_home)
        btn_back.grid(row=0, column=0, sticky="w", padx=10, pady=10)
        
        title = ctk.CTkLabel(self, text="Vos Assistants", font=ctk.CTkFont(size=24, weight="bold"))
        title.grid(row=0, column=0, columnspan=2, pady=(10, 30))

        self.refresh_list()

    def refresh_list(self):
        # Nettoyer (sauf header)
        for widget in self.winfo_children():
            if isinstance(widget, ctk.CTkFrame) and hasattr(widget, "is_card"):
                widget.destroy()

        assistants = self.app.data_manager.get_all_assistants()

        row = 1
        col = 0
        for assistant in assistants:
            self.create_assistant_card(row, col, assistant)
            col += 1
            if col > 1: # 2 colonnes
                col = 0
                row += 1

    def create_assistant_card(self, r, c, assistant):
        card = ctk.CTkFrame(self, corner_radius=15, border_width=1, border_color="gray50")
        card.is_card = True
        card.grid(row=r, column=c, padx=15, pady=15, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)

        # Status
        status_color = "#4CAF50" if assistant["status"] == "running" else "#F44336"
        status_lbl = ctk.CTkLabel(card, text="● " + assistant["status"].upper(), text_color=status_color, font=ctk.CTkFont(size=12, weight="bold"))
        status_lbl.grid(row=0, column=0, sticky="e", padx=15, pady=(10, 0))

        # Nom
        name_lbl = ctk.CTkLabel(card, text=assistant["name"], font=ctk.CTkFont(size=20, weight="bold"))
        name_lbl.grid(row=1, column=0, padx=15, pady=(5, 5))

        desc_lbl = ctk.CTkLabel(card, text=assistant["description"], text_color="gray70")
        desc_lbl.grid(row=2, column=0, padx=15, pady=(0, 15))

        # Actions
        action_frame = ctk.CTkFrame(card, fg_color="transparent")
        action_frame.grid(row=3, column=0, pady=15)

        if assistant["status"] == "running":
            btn_open = ctk.CTkButton(action_frame, text="Ouvrir Interface", width=140, height=35, corner_radius=17,
                                     command=lambda a=assistant: self.app.show_assistant_detail(a))
            btn_open.pack(pady=5)
            
            btn_stop = ctk.CTkButton(action_frame, text="Arrêter", fg_color="transparent", border_width=1, border_color="#F44336", text_color="#F44336", width=140, height=30,
                                     command=lambda a=assistant: self.toggle_status(a, "stopped"))
            btn_stop.pack(pady=5)
        else:
            btn_start = ctk.CTkButton(action_frame, text="Démarrer", fg_color="#4CAF50", hover_color="#388E3C", width=140, height=35, corner_radius=17,
                                      command=lambda a=assistant: self.toggle_status(a, "running"))
            btn_start.pack(pady=5)
            
            btn_del = ctk.CTkButton(action_frame, text="Supprimer", fg_color="transparent", text_color="gray", hover_color="gray20", width=100, height=25,
                                    command=lambda a=assistant: self.delete_assistant(a))
            btn_del.pack(pady=5)

    def toggle_status(self, assistant, new_status):
        self.app.data_manager.update_status(assistant["id"], new_status)
        # Recharger tout le frame pour mettre à jour
        self.app.show_list()

    def delete_assistant(self, assistant):
        if messagebox.askyesno("Confirmer", f"Supprimer {assistant['name']} ?"):
            self.app.data_manager.delete_assistant(assistant["id"])
            self.app.show_list()
