import requests
import os
import sys
import base64
from io import BytesIO
from PIL import Image

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_manager import DataManager

def test_raw_api():
    dm = DataManager()
    settings = dm.get_settings()
    api_keys = settings.get("api_keys", {})
    key = api_keys.get("Hugging Face") or next((v for k, v in api_keys.items() if "Hugging Face" in k), None)
    
    if not key:
        print("No HF key found")
        return

    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {key}"}

    # Create dummy image
    img = Image.new('RGB', (512, 512), color = 'red')
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    # Payload for img2img usually involves sending raw bytes or specific json
    # For HF Inference API, sending raw bytes often defaults to basic classification or similar.
    # But for specialized tasks, we might need to verify the format.
    # However, standard diffusers pipeline on HF Inference API often doesn't support img2img directly via simple raw bytes post if it's text-to-image model.
    # We'll try the common multi-modal format or just binary.
    
    print("Testing Instruct Pix2Pix Raw...")
    
    # Instruct Pix2Pix usually takes:
    # inputs: text prompt
    # image: the input image NOT in inputs but often separate or combined?
    # Actually, often mapped to "inputs" as well?
    # Let's try the standard way HF suggests for multimodal:
    # sending image file bytes as body, and parameters as headers?
    # OR sending json with "inputs" referencing the image?
    
    # Let's try the InferenceClient.post method which handles some auth/etc.
    from huggingface_hub import InferenceClient
    client = InferenceClient(token=key)
    
    model_id = "runwayml/stable-diffusion-v1-5"
    
    # Try sending raw bytes of image + headers for parameters
    try:
        # For legacy SD 1.5 on Inference API, it often accepts just the image bytes as body for "image-to-text" or similar, 
        # but for img2img it's tricky without a specific task endpoint.
        # However, we can try the generic input structure.
        
        payload = {
            "inputs": "A futuristic city",
            "image": img_str
        }
        # Note: often "inputs" is the prompt string. "image" might not be read.
        # Let's try sending parameters.
        
        payload = {
            "inputs": img_str, # Sending image as main input? No, that's for classification.
             "parameters": {
                 "prompt": "A futuristic city"
             }
        }
        
        # ACTUALLY, checking online docs for SD 1.5 Img2Img on HF API:
        # It usually requires using the specific `image-to-image` task which might just be 
        # unavailable.
        
        # Let's try the `client.image_to_image` equivalent via raw post:
        # It sends the image + prompt.
        
        # One last tracked working method for generic models:
        # inputs = prompt
        # parameters = { image: base64 } ? No.
        
        # Let's revert to a simpler test: check if we can even reach the model.
        
        payload = {"inputs": "A cat"} # Text to image check first to verify URL

        
        print(f"Attempting JSON + Base64 payload on {model_id}")
        # Update URL to router.huggingface.co as per error 410
        response = requests.post(
            f"https://router.huggingface.co/models/{model_id}",
            headers=headers,
            json=payload
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        
        if response.status_code == 200:
             print("SUCCESS!")
             # save result
             with open("test_raw_pix2pix.png", "wb") as f:
                 f.write(response.content)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_raw_api()
