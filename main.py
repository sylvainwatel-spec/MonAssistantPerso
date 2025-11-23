import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import os
from data_manager import DataManager

# Configuration du thème
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

LLM_MAPPING = {
    "Google Gemini 1.5 Flash": "gemini-1.5-flash",
    "OpenAI GPT-4o mini": "gpt-4o-mini",
    "Anthropic Claude 3 Haiku": "claude-3-haiku-20240307",
    "Meta Llama 3 (via Groq)": "llama3-8b-8192",
    "Mistral NeMo": "open-mistral-nemo"
}

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Mon Assistant perso")
        self.geometry("900x700")

        self.data_manager = DataManager()

        # Layout principal (1x1) - Navigation plein écran
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.grid(row=0, column=0, sticky="nsew")
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Chargement des ressources
        self.load_resources()

        # Affichage initial
        self.current_frame = None
        self.show_home()

        # Gestion de la fermeture
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        self.destroy()
        self.quit()

    def load_resources(self):
        # Avatar
        img_path = os.path.join(os.path.dirname(__file__), "assistant_avatar.png")
        self.avatar_image = None
        if os.path.exists(img_path):
            try:
                pil_image = Image.open(img_path)
                self.avatar_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(350, 350))
                self.avatar_small = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(60, 60))
            except Exception as e:
                print(f"Erreur image avatar: {e}")
        
        # Settings Icon
        settings_path = os.path.join(os.path.dirname(__file__), "settings_icon.png")
        self.settings_icon = None
        if os.path.exists(settings_path):
            try:
                pil_img = Image.open(settings_path)
                self.settings_icon = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(24, 24))
            except Exception as e:
                print(f"Erreur image settings: {e}")

    def switch_frame(self, frame_class, **kwargs):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = frame_class(self.container, self, **kwargs)
        self.current_frame.grid(row=0, column=0, sticky="nsew")

    def show_home(self):
        self.switch_frame(HomeFrame)

    def show_create(self):
        self.switch_frame(CreateAssistantFrame)

    def show_list(self):
        self.switch_frame(ListAssistantsFrame)

    def show_admin(self):
        self.switch_frame(AdminFrame)
    
    def show_assistant_detail(self, assistant_data):
        self.switch_frame(AssistantDetailFrame, assistant_data=assistant_data)


# --- Vues (Frames) ---

class HomeFrame(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1) # Spacer top
        self.grid_rowconfigure(4, weight=1) # Spacer bottom

        # Admin Button (Top Right)
        if self.app.settings_icon:
            btn_admin = ctk.CTkButton(self, text="", image=self.app.settings_icon, width=40, height=40, 
                                      fg_color="transparent", hover_color=("gray70", "gray30"),
                                      command=self.app.show_admin)
        else:
            btn_admin = ctk.CTkButton(self, text="⚙️", width=40, height=40, 
                                      fg_color="transparent", hover_color=("gray70", "gray30"),
                                      command=self.app.show_admin)
        btn_admin.place(relx=0.95, rely=0.05, anchor="ne")

        # Avatar Central
        if self.app.avatar_image:
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

class AdminFrame(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        
        # --- Data Loading ---
        try:
            self.settings = self.app.data_manager.get_settings()
        except Exception as e:
            print(f"Error loading settings: {e}")
            self.settings = {"current_provider": "OpenAI GPT-4o mini", "api_keys": {}}

        self.active_provider = self.settings.get("current_provider", "OpenAI GPT-4o mini")
        self.api_keys = self.settings.get("api_keys", {})
        
        # List of supported LLMs
        self.llm_options = [
            "Google Gemini 1.5 Flash",
            "OpenAI GPT-4o mini",
            "Anthropic Claude 3 Haiku",
            "Meta Llama 3 (via Groq)",
            "Mistral NeMo"
        ]
        
        # UI State
        self.selected_provider = self.active_provider

        # --- Layout ---
        self.grid_columnconfigure(1, weight=1) # Right panel expands
        self.grid_rowconfigure(1, weight=1)    # Content area expands

        # 1. Header (Top)
        self.create_header()

        # 2. Sidebar (Left) - List of LLMs
        self.sidebar = ctk.CTkScrollableFrame(self, width=250, corner_radius=0, fg_color=("gray90", "gray15"))
        self.sidebar.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        
        # 3. Detail Panel (Right) - Configuration
        self.detail_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.detail_panel.grid(row=1, column=1, sticky="nsew", padx=20, pady=20)
        self.detail_panel.grid_columnconfigure(0, weight=1)

        # Track widgets for safe clearing
        self.sidebar_widgets = []

        # Initial Render
        self.refresh_sidebar()
        self.refresh_detail_panel()

    def create_header(self):
        header = ctk.CTkFrame(self, height=60, corner_radius=0)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=10)
        
        btn_back = ctk.CTkButton(header, text="< Accueil", width=100, height=32, fg_color=("#3B8ED0", "#1F6AA5"), corner_radius=16,
                                 command=self.app.show_home)
        btn_back.pack(side="left", padx=10)
        
        title = ctk.CTkLabel(header, text="Administration & Modèles", font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(side="left", padx=20)

    def refresh_sidebar(self):
        # Clear existing widgets safely
        for widget in self.sidebar_widgets:
            try:
                widget.destroy()
            except:
                pass
        self.sidebar_widgets = []

        lbl = ctk.CTkLabel(self.sidebar, text="Modèles Disponibles", font=ctk.CTkFont(size=14, weight="bold"), text_color="gray60")
        lbl.pack(pady=(10, 5), padx=10, anchor="w")
        self.sidebar_widgets.append(lbl)

        for provider in self.llm_options:
            self.create_sidebar_item(provider)

    def create_sidebar_item(self, provider):
        is_active = (provider == self.active_provider)
        is_selected = (provider == self.selected_provider)
        
        # Style
        btn_color = ("gray80", "gray25") if is_selected else "transparent"
        
        item_frame = ctk.CTkFrame(self.sidebar, fg_color=btn_color, corner_radius=6)
        item_frame.pack(fill="x", padx=5, pady=2)
        self.sidebar_widgets.append(item_frame)
        
        # Click event
        item_frame.bind("<Button-1>", lambda e, p=provider: self.select_provider(p))
        
        # Layout
        item_frame.grid_columnconfigure(1, weight=1)
        
        # Active Indicator
        indicator_color = "#4CAF50" if is_active else "transparent"
        indicator = ctk.CTkLabel(item_frame, text="●", text_color=indicator_color, font=ctk.CTkFont(size=16))
        indicator.grid(row=0, column=0, padx=(10, 5), pady=10)
        indicator.bind("<Button-1>", lambda e, p=provider: self.select_provider(p))

        # Name
        name_font = ctk.CTkFont(size=13, weight="bold" if is_active else "normal")
        lbl_name = ctk.CTkLabel(item_frame, text=provider, font=name_font)
        lbl_name.grid(row=0, column=1, sticky="w", padx=5)
        lbl_name.bind("<Button-1>", lambda e, p=provider: self.select_provider(p))
        
        # Active Badge
        if is_active:
            lbl_status = ctk.CTkLabel(item_frame, text="ACTIF", font=ctk.CTkFont(size=10, weight="bold"), text_color="#4CAF50")
            lbl_status.grid(row=0, column=2, padx=10)
            lbl_status.bind("<Button-1>", lambda e, p=provider: self.select_provider(p))

    def select_provider(self, provider):
        self.selected_provider = provider
        self.refresh_sidebar()
        self.refresh_detail_panel()

    def refresh_detail_panel(self):
        # Clear existing
        for widget in self.detail_panel.winfo_children():
            widget.destroy()
            
        if not self.selected_provider:
            return

        # Header
        ctk.CTkLabel(self.detail_panel, text=self.selected_provider, font=ctk.CTkFont(size=24, weight="bold")).pack(anchor="w", pady=(0, 5))
        
        if self.selected_provider == self.active_provider:
            ctk.CTkLabel(self.detail_panel, text="✅ Ce modèle est actuellement utilisé par défaut.", text_color="#4CAF50").pack(anchor="w", pady=(0, 20))
        else:
            ctk.CTkLabel(self.detail_panel, text="Ce modèle n'est pas actif.", text_color="gray").pack(anchor="w", pady=(0, 20))

        # API Key Section
        key_frame = ctk.CTkFrame(self.detail_panel)
        key_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(key_frame, text="Clé API", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20, pady=(15, 5))
        
        current_key = self.api_keys.get(self.selected_provider, "")
        self.entry_key = ctk.CTkEntry(key_frame, width=400, show="*")
        self.entry_key.insert(0, current_key)
        self.entry_key.pack(padx=20, pady=5, fill="x")
        
        btn_save_key = ctk.CTkButton(key_frame, text="Enregistrer la clé", width=150, 
                                     command=self.save_current_key)
        btn_save_key.pack(anchor="e", padx=20, pady=(10, 15))

        # Activation Section
        if self.selected_provider != self.active_provider:
            action_frame = ctk.CTkFrame(self.detail_panel, fg_color="transparent")
            action_frame.pack(fill="x", pady=30)
            
            lbl_info = ctk.CTkLabel(action_frame, text="Voulez-vous utiliser ce modèle pour tous vos assistants ?", text_color="gray")
            lbl_info.pack(anchor="w", pady=(0, 10))
            
            btn_activate = ctk.CTkButton(action_frame, text="Définir comme Modèle par Défaut", 
                                         fg_color="#4CAF50", hover_color="#388E3C", height=40,
                                         font=ctk.CTkFont(weight="bold"),
                                         command=self.set_as_active)
            btn_activate.pack(fill="x")

    def save_current_key(self):
        new_key = self.entry_key.get().strip()
        self.api_keys[self.selected_provider] = new_key
        
        try:
            self.app.data_manager.save_configuration(self.active_provider, self.api_keys)
            messagebox.showinfo("Succès", f"Clé API pour {self.selected_provider} enregistrée.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde : {e}")

    def set_as_active(self):
        # Save key first if changed
        current_input_key = self.entry_key.get().strip()
        if current_input_key != self.api_keys.get(self.selected_provider, ""):
            self.api_keys[self.selected_provider] = current_input_key
            
        self.active_provider = self.selected_provider
        try:
            self.app.data_manager.save_configuration(self.active_provider, self.api_keys)
            self.refresh_sidebar()
            self.refresh_detail_panel()
            messagebox.showinfo("Succès", f"{self.active_provider} est maintenant le modèle par défaut.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'activation : {e}")


if __name__ == "__main__":
    app = App()
    app.mainloop()
