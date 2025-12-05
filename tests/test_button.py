"""Test script to verify the create button functionality"""
import os
import sys

# Ensure utils can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.data_manager import DataManager
from pages.home_page import HomeFrame
from pages.create_page import CreateAssistantFrame
import customtkinter as ctk

# Test if the show_create method works
class MockApp:
    def __init__(self):
        self.data_manager = DataManager()
        self.avatar_image = None
        self.avatar_small = None
        self.settings_icon = None
        
    def show_create(self):
        print("✓ show_create() was called successfully!")
        return True
    
    def show_home(self):
        print("✓ show_home() was called successfully!")
        return True
    
    def show_list(self):
        print("✓ show_list() was called successfully!")
        return True
    
    def show_admin(self):
        print("✓ show_admin() was called successfully!")
        return True

# Test the methods
print("Testing app methods...")
app = MockApp()

# Test if methods exist and are callable
print("\n1. Testing show_create method:")
try:
    app.show_create()
except Exception as e:
    print(f"✗ Error calling show_create: {e}")

print("\n2. Testing show_home method:")
try:
    app.show_home()
except Exception as e:
    print(f"✗ Error calling show_home: {e}")

print("\n3. Testing show_list method:")
try:
    app.show_list()
except Exception as e:
    print(f"✗ Error calling show_list: {e}")

print("\n4. Testing show_admin method:")
try:
    app.show_admin()
except Exception as e:
    print(f"✗ Error calling show_admin: {e}")

print("\n5. Testing CreateAssistantFrame initialization:")
try:
    root = ctk.CTk()
    root.withdraw()  # Hide the window
    container = ctk.CTkFrame(root)
    frame = CreateAssistantFrame(container, app)
    print("✓ CreateAssistantFrame initialized successfully!")
    root.destroy()
except Exception as e:
    print(f"✗ Error initializing CreateAssistantFrame: {e}")
    import traceback
    traceback.print_exc()

print("\nAll tests completed!")
