import PyInstaller.__main__
import os
import customtkinter
import sys

def build():
    print("Building executable...")
    
    # Get customtkinter path for data collection
    ctk_path = os.path.dirname(customtkinter.__file__)
    
    # Define assets to include
    # Format: "source;dest" for Windows
    assets = [
        "assistant_avatar.png;.",
        "settings_icon.png;.",
        f"{ctk_path};customtkinter"
    ]
    
    args = [
        'main.py',
        '--name=MonAssistantPerso',
        '--onefile',
        '--noconsole',  # Hide console window
        '--clean',
        # Exclude unnecessary modules to save space
        '--exclude-module=tkinter.test',
        '--exclude-module=unittest',
    ]
    
    for asset in assets:
        args.append(f'--add-data={asset}')
        
    # Add hidden imports that might be missed
    hidden_imports = [
        'PIL._tkinter_finder',
        'playwright',
        'playwright.sync_api',
    ]
    for hidden in hidden_imports:
        args.append(f'--hidden-import={hidden}')

    PyInstaller.__main__.run(args)
    
    print("Build complete. Check 'dist' folder.")

if __name__ == "__main__":
    build()
