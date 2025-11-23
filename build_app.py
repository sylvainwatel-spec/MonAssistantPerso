import PyInstaller.__main__
import os

def build():
    print("Building executable...")
    
    # Define assets to include
    # Format: "source;dest" for Windows
    assets = [
        "assistant_avatar.png;.",
        "settings_icon.png;."
    ]
    
    args = [
        'main.py',
        '--name=MonAssistantPerso',
        '--onefile',
        '--noconsole',  # Hide console window
        '--clean',
    ]
    
    for asset in assets:
        args.append(f'--add-data={asset}')
        
    PyInstaller.__main__.run(args)
    
    print("Build complete. Check 'dist' folder.")

if __name__ == "__main__":
    build()
