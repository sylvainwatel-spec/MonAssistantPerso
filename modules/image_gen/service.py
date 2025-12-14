import os
import requests
from openai import OpenAI
from io import BytesIO
from PIL import Image
from typing import Tuple, Any
from huggingface_hub import InferenceClient
try:
    import torch
    from diffusers import QwenImageEditPlusPipeline
except ImportError:
    torch = None
    QwenImageEditPlusPipeline = None

class ImageGenerationService:
    """Service for generating images using various providers."""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
        
        self.hf_models = {
            "Stable Diffusion XL": "stabilityai/stable-diffusion-xl-base-1.0",
            "FLUX.1 [schnell]": "black-forest-labs/FLUX.1-schnell",
            "Stable Diffusion 3.5 Large": "stabilityai/stable-diffusion-3.5-large",
        }

    def generate_image(self, prompt: str, provider: str = "OpenAI DALL-E 3", size: str = "1024x1024", image_path: str = None, image_path_2: str = None) -> Tuple[bool, Any, str]:
        """
        Generates an image from a prompt (and optional input image).
        
        Returns:
            Tuple (success, image_object, message_or_path)
            image_object: PIL Image object or None
            message_or_path: Error message or description
        """
        settings = self.data_manager.get_settings()
        api_keys = settings.get("api_keys", {})
        
        if "OpenAI" in provider:
            if image_path:
                return False, None, "DALL-E 3 ne supporte pas l'édition d'image (Image-to-Image). Veuillez utiliser un modèle compatible (marqué Image-to-Image)."
                
            key = api_keys.get("OpenAI GPT-4o mini") # Reuse OpenAI key
            if not key:
                 # Try finding any key with OpenAI in it
                key = next((v for k, v in api_keys.items() if "OpenAI" in k), None)
            
            if not key:
                return False, None, "Clé API OpenAI non trouvée. Veuillez configurer OpenAI dans l'administration."
                
            try:
                client = OpenAI(api_key=key)
                
                model = "dall-e-3" if "DALL-E 3" in provider else "dall-e-2"
                
                response = client.images.generate(
                    model=model,
                    prompt=prompt,
                    size=size,
                    quality="standard",
                    n=1,
                )
                
                image_url = response.data[0].url
                
                # Download image
                img_response = requests.get(image_url)
                img = Image.open(BytesIO(img_response.content))
                
                return True, img, "Image générée avec succès"
                
            except Exception as e:
                return False, None, f"Erreur lors de la génération avec OpenAI : {str(e)}"
                
        elif provider == "Qwen-Image-Edit-2509":
             return self._generate_qwen(prompt, image_path, image_path_2)

        elif provider in self.hf_models:
             return self._generate_hf(prompt, provider, api_keys, image_path)
        
        return False, None, f"Provider {provider} non supporté pour le moment."

    def _generate_qwen(self, prompt: str, image_path: str, image_path_2: str = None) -> Tuple[bool, Any, str]:
        """Generate image using local Qwen-Image-Edit-2509 pipeline."""
        if not image_path or not os.path.exists(image_path):
             return False, None, "Une image source est requise pour Qwen-Image-Edit."
             
        if QwenImageEditPlusPipeline is None:
             return False, None, "La librairie 'diffusers' n'est pas installée correctement pour Qwen."

        try:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"DEBUG: Qwen loading on {device}...")
            
            # Using torch.float32 for CPU compatibility if fallback, but snippet used bfloat16.
            # bfloat16 requires CUDA or specific CPU support. safer to use float16 on cuda or float32 on cpu.
            dtype = torch.bfloat16 if device == "cuda" else torch.float32
            
            pipeline = QwenImageEditPlusPipeline.from_pretrained(
                "Qwen/Qwen-Image-Edit-2509", 
                torch_dtype=dtype
            )
            pipeline.to(device)
            # pipeline.set_progress_bar_config(disable=None) # Optional

            source_image = Image.open(image_path).convert("RGB") # Ensure RGB
            
            if image_path_2 and os.path.exists(image_path_2):
                source_image_2 = Image.open(image_path_2).convert("RGB")
            else:
                source_image_2 = source_image # Fallback to single image if strictly required by logic or just use same
            
            inputs = {
                "image": [source_image, source_image_2],
                "prompt": prompt,
                "generator": torch.manual_seed(42),
                "true_cfg_scale": 4.0,
                "negative_prompt": " ",
                "num_inference_steps": 40,
                "guidance_scale": 1.0, 
                "num_images_per_prompt": 1,
            }

            with torch.inference_mode():
                output = pipeline(**inputs)
                final_image = output.images[0]
                
            return True, final_image, "Image éditée avec succès (Qwen Local)"

        except Exception as e:
            import traceback
            traceback.print_exc()
            return False, None, f"Erreur Qwen Local : {str(e)}"

    def _generate_hf(self, prompt: str, provider: str, api_keys: dict, image_path: str = None) -> Tuple[bool, Any, str]:
        """Generate image using Hugging Face Inference API."""
        key = api_keys.get("Hugging Face")
        if not key:
            key = next((v for k, v in api_keys.items() if "Hugging Face" in k), None)
            
        if not key:
             return False, None, "Clé API Hugging Face non trouvée. Veuillez la configurer dans l'administration (Chat)."

        model_id = self.hf_models.get(provider)
        
        try:
            # Use standard InferenceClient
            client = InferenceClient(token=key)
            
            print(f"DEBUG: Using HF Key (masked): {key[:4]}...{key[-4:] if key else 'None'}")
            print(f"DEBUG: Model ID: {model_id}")
            print(f"DEBUG: Provider: {provider}")
            
            if image_path:
                # Image-to-Image mode
                print(f"DEBUG: Image-to-Image mode with path: {image_path}")
                if not os.path.exists(image_path):
                     return False, None, "L'image source n'existe pas."
                
                source_image = Image.open(image_path)
                print(f"DEBUG: Image loaded: {source_image.size}")
                
                # Force specific handling for known img2img models to avoid auto-mapping issues?
                # The client.image_to_image should work if the model supports it.
                try:
                    image = client.image_to_image(image=source_image, prompt=prompt, model=model_id)
                except StopIteration:
                     return False, None, f"Ce modèle ({provider}) ne semble pas supporter l'Image-to-Image via l'API gratuite actuelle. Essayez 'Instruct Pix2Pix' ou 'SD 1.5'."
                except Exception as e:
                     if "404" in str(e) or "410" in str(e):
                          return False, None, f"Le service pour {provider} est actuellement indisponible ou a changé d'adresse (Erreur API)."
                     if "503" in str(e):
                          return False, None, f"Le modèle {provider} est en cours de chargement (503). Réessayez dans 30 secondes."
                     raise e
                     
                success_msg = f"Image modifiée avec succès ({provider})"
            else:
                # Text-to-Image mode
                image = client.text_to_image(prompt, model=model_id)
                success_msg = f"Image générée avec succès ({provider})"
                
            return True, image, success_msg
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"DEBUG: Full Error: {e}")
            return False, None, f"Erreur Hugging Face ({provider}) : {str(e)}"
