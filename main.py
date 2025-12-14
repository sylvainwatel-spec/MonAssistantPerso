import os
import sys
from typing import Optional, Any, Type

import customtkinter as ctk
from PIL import Image

# Ensure utils can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.data_manager import DataManager
from utils.resource_handler import resource_path
from modules.assistants.home import HomeFrame
from modules.assistants.create import CreateAssistantFrame
from modules.assistants.list import ListAssistantsFrame
from modules.settings.view import AdminFrame
from modules.assistants.detail import AssistantDetailFrame
from modules.assistants.chat import ChatFrame
from modules.settings.chat_connector import ChatConnectorFrame
from modules.settings.scraping_connector import ScrapeGraphConnectorFrame
from utils.plugin_manager import manager
from modules.image_gen.view import ImageGenFrame
from modules.doc_analyst.view import DocAnalystFrame
from modules.data_viz.view import DataVizFrame
from modules.financial.view import FinancialAnalysisFrame
from modules.scraping.view import ScrapingFrame

# Register pages with PluginManager
manager.register('home', HomeFrame)
manager.register('create', CreateAssistantFrame)
manager.register('list', ListAssistantsFrame)
manager.register('admin', AdminFrame)
manager.register('detail', AssistantDetailFrame)
manager.register('chat', ChatFrame)
manager.register('connector', ChatConnectorFrame)
manager.register('scrapegraph', ScrapeGraphConnectorFrame)
manager.register('image_gen', ImageGenFrame)
manager.register('doc_analyst', DocAnalystFrame)
manager.register('data_viz', DataVizFrame)
manager.register('financial', FinancialAnalysisFrame)
manager.register('scraping', ScrapingFrame)

# Configuration du thème
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        self.title("Mon Assistant perso")
        width = 1100
        height = 850
        
        # Center the window
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = int((screen_width / 2) - (width / 2))
        y = int((screen_height / 2) - (height / 2))
        
        # Ensure y is not negative
        y = max(0, y)

        self.geometry(f"{width}x{height}+{x}+{y}")
        
        # Icon setup
        try:
            icon_path = resource_path(os.path.join("image", "settings_icon.png"))
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except Exception:
            pass

        self.data_manager = DataManager()

        # Layout principal (1x1) - Navigation plein écran
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.grid(row=0, column=0, sticky="nsew")
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Configuration du fond d'écran global
        self._setup_background_image()

        # Chargement des ressources
        self.load_resources()

        # Affichage initial
        self.current_frame: Optional[ctk.CTkFrame] = None
        self.show_home()

        # Gestion de la fermeture
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self) -> None:
        self.destroy()
        self.quit()

    def _setup_background_image(self) -> None:
        """Sets up the global background image."""
        bg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "image", "Page_accueil.png")
        if os.path.exists(bg_path):
            try:
                # Load and ensure opaque
                bg_image = Image.open(bg_path).convert("RGB")
                
                self.bg_ctk_image = ctk.CTkImage(
                    light_image=bg_image,
                    dark_image=bg_image,
                    size=(1100, 850) # Match initial window size
                )

                self.bg_label = ctk.CTkLabel(self, text="", image=self.bg_ctk_image)
                self.bg_label.place(relx=0, rely=0, relwidth=1, relheight=1)
                # Ensure background is behind the main container
                self.bg_label.lower(self.container)
                print("DEBUG: Global background setup complete.")
            except Exception as e:
                print(f"Error setting up background: {e}")

    def load_resources(self) -> None:
        # Avatar
        img_path = resource_path(os.path.join("image", "assistant_avatar.png"))
        self.avatar_image = None
        self.avatar_small = None
        
        if os.path.exists(img_path):
            try:
                pil_image = Image.open(img_path)
                self.avatar_pil = pil_image # Store original for manipulations
                self.avatar_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(350, 350))
                self.avatar_small = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(60, 60))
            except Exception as e:
                print(f"Erreur image avatar: {e}")
                self.avatar_pil = None
        
        # Home Background
        bg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "image", "Page_accueil.png")
        self.background_pil = None
        if os.path.exists(bg_path):
            try:
                print(f"DEBUG: Loading background from {bg_path}")
                self.background_pil = Image.open(bg_path)
            except Exception as e:
                print(f"Erreur image background: {e}")
        else:
            print(f"DEBUG: Background file not found at {bg_path}")

        # Settings Icon
        settings_path = resource_path(os.path.join("image", "settings_icon.png"))
        self.settings_icon = None
        if os.path.exists(settings_path):
            try:
                pil_img = Image.open(settings_path)
                self.settings_icon = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(24, 24))
            except Exception as e:
                print(f"Erreur image settings: {e}")

    def switch_frame(self, frame_class: Type[ctk.CTkFrame], **kwargs: Any) -> None:
        try:
            if self.current_frame:
                self.current_frame.destroy()
            self.current_frame = frame_class(self.container, self, **kwargs)
            self.current_frame.grid(row=0, column=0, sticky="nsew")
        except Exception as e:
            print(f"ERROR in switch_frame: {e}")
            import traceback
            traceback.print_exc()
            # Show error to user
            from tkinter import messagebox
            messagebox.showerror("Erreur", f"Impossible de charger la page: {e}")

    def show_home(self) -> None:
        self.switch_frame(manager.get('home'))

    def show_create(self) -> None:
        self.switch_frame(manager.get('create'))

    def show_list(self) -> None:
        self.switch_frame(manager.get('list'))

    def show_admin(self) -> None:
        self.switch_frame(manager.get('admin'))
    
    def show_chat_connector(self) -> None:
        self.switch_frame(manager.get('connector'))
    
    def show_scrapegraph_connector(self) -> None:
        self.switch_frame(manager.get('scrapegraph'))
    
    def show_assistant_detail(self, assistant_data: Any) -> None:
        self.switch_frame(manager.get('detail'), assistant_data=assistant_data)
    
    def show_chat(self, assistant_data: Any) -> None:
        self.switch_frame(manager.get('chat'), assistant_data=assistant_data)

    def show_image_gen(self) -> None:
        self.switch_frame(manager.get('image_gen'))

    def show_doc_analyst(self) -> None:
        self.switch_frame(manager.get('doc_analyst'))

    def show_data_viz(self) -> None:
        self.switch_frame(manager.get('data_viz'))

    def show_financial(self) -> None:
        self.switch_frame(manager.get('financial'))

    def show_scraping(self) -> None:
        self.switch_frame(manager.get('scraping'))

if __name__ == "__main__":
    app = App()
    app.mainloop()
