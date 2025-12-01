import os
import sys
from typing import Optional, Any, Type

import customtkinter as ctk
from PIL import Image

# Ensure utils can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.data_manager import DataManager
from utils.resource_handler import resource_path
from pages.home_page import HomeFrame
from pages.create_page import CreateAssistantFrame
from pages.list_page import ListAssistantsFrame
from pages.admin_page import AdminFrame
from pages.detail_page import AssistantDetailFrame
from pages.chat_page import ChatFrame
from pages.chat_connector_page import ChatConnectorFrame
from pages.scrapegraph_connector_page import ScrapeGraphConnectorFrame

# Configuration du thème
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        self.title("Mon Assistant perso")
        self.geometry("900x700")
        
        # Icon setup
        try:
            icon_path = resource_path("settings_icon.png")
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

    def load_resources(self) -> None:
        # Avatar
        img_path = resource_path("assistant_avatar.png")
        self.avatar_image = None
        self.avatar_small = None
        
        if os.path.exists(img_path):
            try:
                pil_image = Image.open(img_path)
                self.avatar_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(350, 350))
                self.avatar_small = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(60, 60))
            except Exception as e:
                print(f"Erreur image avatar: {e}")
        
        # Settings Icon
        settings_path = resource_path("settings_icon.png")
        self.settings_icon = None
        if os.path.exists(settings_path):
            try:
                pil_img = Image.open(settings_path)
                self.settings_icon = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(24, 24))
            except Exception as e:
                print(f"Erreur image settings: {e}")

    def switch_frame(self, frame_class: Type[ctk.CTkFrame], **kwargs: Any) -> None:
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = frame_class(self.container, self, **kwargs)
        self.current_frame.grid(row=0, column=0, sticky="nsew")

    def show_home(self) -> None:
        self.switch_frame(HomeFrame)

    def show_create(self) -> None:
        self.switch_frame(CreateAssistantFrame)

    def show_list(self) -> None:
        self.switch_frame(ListAssistantsFrame)

    def show_admin(self) -> None:
        self.switch_frame(AdminFrame)
    
    def show_chat_connector(self) -> None:
        self.switch_frame(ChatConnectorFrame)
    
    def show_scrapegraph_connector(self) -> None:
        self.switch_frame(ScrapeGraphConnectorFrame)
    
    def show_assistant_detail(self, assistant_data: Any) -> None:
        self.switch_frame(AssistantDetailFrame, assistant_data=assistant_data)
    
    def show_chat(self, assistant_data: Any) -> None:
        self.switch_frame(ChatFrame, assistant_data=assistant_data)

if __name__ == "__main__":
    app = App()
    app.mainloop()
