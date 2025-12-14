import sys
print(f"Python executable: {sys.executable}")
try:
    import torch
    print(f"Torch version: {torch.__version__}")
    from diffusers import QwenImageEditPlusPipeline
    print("Diffusers imported successfully")
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Error: {e}")
