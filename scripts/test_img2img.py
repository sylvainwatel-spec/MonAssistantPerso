import sys
import os
from PIL import Image

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.image_gen.service import ImageGenerationService
from utils.data_manager import DataManager

def test_img2img():
    print("--- Testing Image-to-Image Service Logic ---")
    
    # 1. Create dummy image
    img_path = "test_source.png"
    img = Image.new('RGB', (512, 512), color = 'red')
    img.save(img_path)
    print(f"Created dummy image: {img_path}")
    
    dm = DataManager()
    service = ImageGenerationService(dm)
    
    # 2. Test with DALL-E 3 (Should fail)
    print("\nTesting DALL-E 3 with image...")
    success, _, msg = service.generate_image("test", provider="OpenAI DALL-E 3", image_path=img_path)
    print(f"Result: {success}, Message: {msg}")
    if not success and "ne supporte pas" in msg:
        print("✅ Correctly rejected DALL-E 3")
    else:
        print("❌ Unexpected result for DALL-E 3")

    # 3. Test candidate models for Img2Img support
    print("\n--- Testing Candidate Models for Image-to-Image ---")
    
    candidate_models = {
        "Stable Diffusion 1.5 (Image-to-Image)": "runwayml/stable-diffusion-v1-5",
        "Instruct Pix2Pix (Image-to-Image)": "timbrooks/instruct-pix2pix"
    }
    
    # Reload service to get updated simple keys if we were testing valid ones
    # But here we are testing the keys as they are in the service now.
    
    for name, model_id in candidate_models.items():
        print(f"\nTesting provider: {name}...")
        
        # We don't need to manually inject into service.hf_models anymore if they are there,
        # but let's just call generate_image with the new provider names.
        
        success, res_img, msg = service.generate_image("A futuristic city", provider=name, image_path=img_path)
        
        print(f"Result for {name}: {success}")
        if success:
             print(f"✅ {name} Success!")
             res_img.save(f"test_result_{name.replace(' ', '_')}.png")
        else:
             print(f"❌ {name} Failed: {msg}")

    # Cleanup
    if os.path.exists(img_path):
        os.remove(img_path)

if __name__ == "__main__":
    test_img2img()
