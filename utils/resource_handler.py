import sys
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def get_writable_path(filename):
    """ Get path for writable files (data), works for dev and PyInstaller """
    # For a portable app, we want data next to the executable
    if getattr(sys, 'frozen', False):
        # If running as compiled exe
        base_path = os.path.dirname(sys.executable)
    else:
        # If running as script
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, filename)
