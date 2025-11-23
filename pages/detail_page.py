import customtkinter as ctk

class AssistantDetailFrame(ctk.CTkFrame):
    def __init__(self, master, app, assistant_data):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.assistant = assistant_data
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        header = ctk.CTkFrame(self, height=60, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")
        
        btn_back = ctk.CTkButton(header, text="< Retour", width=100, height=32, fg_color=("#3B8ED0", "#1F6AA5"), corner_radius=16, 
                                 command=self.app.show_list)
        btn_back.pack(side="left", padx=20, pady=10)
        
        title = ctk.CTkLabel(header, text=self.assistant['name'], font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(side="left", padx=20)

        # Chat Area
        self.chat_area = ctk.CTkTextbox(self, state="disabled", font=ctk.CTkFont(size=14))
        self.chat_area.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        
        self.log_message(f"Système : Connexion à {self.assistant['name']} établie.")

        # Input Area
        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.grid(row=2, column=0, padx=20, pady=20, sticky="ew")
        input_frame.grid_columnconfigure(0, weight=1)

        self.entry = ctk.CTkEntry(input_frame, placeholder_text="Message...", height=50, corner_radius=25)
        self.entry.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        self.entry.bind("<Return>", self.send_message)

        btn_send = ctk.CTkButton(input_frame, text="Envoyer", width=100, height=50, corner_radius=25,
                                 command=self.send_message_btn)
        btn_send.grid(row=0, column=1)

    def send_message_btn(self):
        self.send_message(None)

    def send_message(self, event):
        msg = self.entry.get()
        if msg:
            self.log_message(f"Vous : {msg}")
            self.log_message(f"{self.assistant['name']} : Je suis à votre écoute.")
            self.entry.delete(0, "end")

    def log_message(self, text):
        self.chat_area.configure(state="normal")
        self.chat_area.insert("end", text + "\n\n")
        self.chat_area.configure(state="disabled")
        self.chat_area.see("end")
