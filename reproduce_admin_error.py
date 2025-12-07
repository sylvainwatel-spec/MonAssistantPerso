import customtkinter as ctk
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from pages.admin_page import AdminFrame
from utils.data_manager import DataManager

class MockApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.data_manager = DataManager()
        self.show_home = lambda: print("Show Home")
        self.show_scrapegraph_connector = lambda: print("Show ScrapeGraph Connect")
        self.show_chat_connector = lambda: print("Show Chat Connect")
        
        # Mock data manager specifically if needed, but we use real DataManager instance above
        # However, DataManager needs files.
        # Ensure DataManager has methods mocked if they depend on files not present?
        # DataManager is imported from utils.data_manager. It should work if files exist or default.


print("Starting reproduction test...")
app = MockApp()
try:
    frame = AdminFrame(app, app)
    frame.pack()
    print("AdminFrame created successfully")
except Exception as e:
    print(f"Error creating AdminFrame: {e}")
    import traceback
    traceback.print_exc()

app.update()
app.destroy()
print("Test finished")
