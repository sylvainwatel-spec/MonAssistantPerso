"""Automated test to click the create button and see if any errors occur"""
import os
import sys
import customtkinter as ctk
from PIL import Image

# Ensure utils can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.data_manager import DataManager
from utils.resource_handler import resource_path
from pages.home_page import HomeFrame
from pages.create_page import CreateAssistantFrame

class AutoTestApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Auto Test - Create Button")
        self.geometry("900x700")
        
        self.data_manager = DataManager()
        
        # Layout principal
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.grid(row=0, column=0, sticky="nsew")
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        # Load resources
        self.load_resources()
        
        # Current frame
        self.current_frame = None
        
        # Show home
        print("1. Showing home frame...")
        self.show_home()
        
        # Schedule automatic test
        self.after(1500, self.auto_test_create_button)
        
    def load_resources(self):
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
                print(f"Error loading avatar: {e}")
        
        # Settings Icon
        settings_path = resource_path("settings_icon.png")
        self.settings_icon = None
        if os.path.exists(settings_path):
            try:
                pil_img = Image.open(settings_path)
                self.settings_icon = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(24, 24))
            except Exception as e:
                print(f"Error loading settings icon: {e}")
    
    def switch_frame(self, frame_class, **kwargs):
        try:
            print(f"   - Destroying old frame...")
            if self.current_frame:
                self.current_frame.destroy()
            print(f"   - Creating new frame: {frame_class.__name__}")
            self.current_frame = frame_class(self.container, self, **kwargs)
            print(f"   - Gridding new frame...")
            self.current_frame.grid(row=0, column=0, sticky="nsew")
            print(f"   ✓ Frame switched successfully to {frame_class.__name__}")
        except Exception as e:
            print(f"   ✗ ERROR in switch_frame: {e}")
            import traceback
            traceback.print_exc()
            from tkinter import messagebox
            messagebox.showerror("Erreur", f"Impossible de charger la page: {e}")
    
    def show_home(self):
        print("   show_home() called")
        self.switch_frame(HomeFrame)
    
    def show_create(self):
        print("2. show_create() called!")
        self.switch_frame(CreateAssistantFrame)
        # If we get here, the frame was created successfully
        print("3. ✓✓✓ SUCCESS! CreateAssistantFrame loaded!")
        self.after(1000, self.quit)
    
    def show_list(self):
        print("   show_list() called")
    
    def show_admin(self):
        print("   show_admin() called")
    
    def auto_test_create_button(self):
        print("\n2. Auto-clicking the create button...")
        try:
            self.show_create()
        except Exception as e:
            print(f"✗ Error calling show_create: {e}")
            import traceback
            traceback.print_exc()
            self.after(1000, self.quit)

if __name__ == "__main__":
    print("="*60)
    print("AUTOMATED TEST: Create Button")
    print("="*60)
    app = AutoTestApp()
    app.mainloop()
    print("\nTest completed!")
