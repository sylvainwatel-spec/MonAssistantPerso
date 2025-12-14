import os
import sys
from PIL import Image
from huggingface_hub import InferenceClient

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_manager import DataManager

def test_client_init():
    dm = DataManager()
    settings = dm.get_settings()
    api_keys = settings.get("api_keys", {})
    key = api_keys.get("Hugging Face") or next((v for k, v in api_keys.items() if "Hugging Face" in k), None)
    
    if not key:
        print("No HF key found")
        return

    model_id = "runwayml/stable-diffusion-v1-5"
    print(f"Testing direct client init with: {model_id}")
    
    try:
        # Initialize client WITH model
        client = InferenceClient(model=model_id, token=key)
        
        # Create dummy image
        img = Image.new('RGB', (512, 512), color = 'red')
        
        print("Attempting image_to_image...")
        # Note: image_to_image method signature might change if model is pre-set? 
        # Usually it's client.image_to_image(image, prompt)
        
        res = client.image_to_image(
            image=img,
            prompt="turn it blue"
        )
        print("SUCCESS!")
        res.save("test_client_init_result.png")
        
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_client_init()
