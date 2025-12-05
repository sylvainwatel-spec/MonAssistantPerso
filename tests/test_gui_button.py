"""Test the actual GUI button click"""
import os
import sys
import customtkinter as ctk

# Ensure utils can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.data_manager import DataManager
from utils.resource_handler import resource_path
from pages.home_page import HomeFrame
from PIL import Image

class TestApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Test Create Button")
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
        
        # Track if show_create was called
        self.create_called = False
        
        # Show home frame
        self.current_frame = HomeFrame(self.container, self)
        self.current_frame.grid(row=0, column=0, sticky="nsew")
        
        # Schedule button click test
        self.after(1000, self.test_button_click)
        
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
    
    def show_create(self):
        print("✓✓✓ SUCCESS! show_create() was called!")
        self.create_called = True
        self.after(500, self.quit)
    
    def show_home(self):
        print("show_home() called")
    
    def show_list(self):
        print("show_list() called")
    
    def show_admin(self):
        print("show_admin() called")
    
    def test_button_click(self):
        print("\nSearching for the create button...")
        # Find the create button and simulate a click
        try:
            # The button should be in the dock_frame
            for widget in self.current_frame.winfo_children():
                if isinstance(widget, ctk.CTkFrame):
                    for child in widget.winfo_children():
                        if isinstance(child, ctk.CTkButton):
                            button_text = child.cget("text")
                            print(f"Found button: '{button_text}'")
                            if "+ Créer" in button_text or "Créer" in button_text:
                                print(f"Found create button! Clicking it...")
                                child.invoke()
                                return
            
            print("✗ Create button not found!")
            self.after(500, self.quit)
        except Exception as e:
            print(f"✗ Error during button test: {e}")
            import traceback
            traceback.print_exc()
            self.after(500, self.quit)

if __name__ == "__main__":
    print("Starting GUI test...")
    app = TestApp()
    app.mainloop()
    
    if app.create_called:
        print("\n✓✓✓ TEST PASSED: Button works correctly!")
    else:
        print("\n✗✗✗ TEST FAILED: Button did not trigger show_create()")
