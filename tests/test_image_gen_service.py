import unittest
from unittest.mock import MagicMock, patch
import os
import sys

# Ensure modules can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.image_gen.service import ImageGenerationService

class TestImageGenerationService(unittest.TestCase):
    def setUp(self):
        self.mock_data_manager = MagicMock()
        self.mock_data_manager.get_settings.return_value = {
            "api_keys": {
                "OpenAI GPT-4o mini": "sk-test-key", 
                "Hugging Face": "hf_test_token"
            },
            "image_gen_provider": "OpenAI DALL-E 3"
        }
        self.service = ImageGenerationService(self.mock_data_manager)

    @patch('modules.image_gen.service.OpenAI')
    @patch('modules.image_gen.service.requests.get')
    def test_generate_image_openai_success(self, mock_get, mock_openai):
        # Mock OpenAI response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [MagicMock(url="http://test.com/image.png")]
        mock_client.images.generate.return_value = mock_response
        mock_openai.return_value = mock_client

        # Mock Image download
        mock_img_response = MagicMock()
        mock_img_response.content = b'fake-image-content'
        mock_get.return_value = mock_img_response

        with patch('modules.image_gen.service.Image.open') as mock_img_open:
            mock_img_open.return_value = "VerifiedImageObject"
            
            success, img, msg = self.service.generate_image("A test prompt", provider="OpenAI DALL-E 3")
            
            self.assertTrue(success)
            self.assertEqual(img, "VerifiedImageObject")
            self.assertIn("succès", msg)

    def test_generate_image_no_key(self):
        self.mock_data_manager.get_settings.return_value = {
            "api_keys": {}, # No keys
            "image_gen_provider": "OpenAI DALL-E 3"
        }
        success, img, msg = self.service.generate_image("test")
        self.assertFalse(success)
        self.assertIn("non trouvée", msg)

    @patch('modules.image_gen.service.OpenAI')
    def test_generate_image_openai_error(self, mock_openai):
        mock_client = MagicMock()
        mock_client.images.generate.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client

        success, img, msg = self.service.generate_image("test", provider="OpenAI DALL-E 3")
        self.assertFalse(success)
        self.assertIn("API Error", msg)

    @patch('modules.image_gen.service.InferenceClient')
    def test_generate_image_hf_text_to_image(self, mock_inference_client):
        # Setup Mock
        mock_client_instance = MagicMock()
        mock_inference_client.return_value = mock_client_instance
        
        expected_image = "HF_Image_Object"
        mock_client_instance.text_to_image.return_value = expected_image
        
        # Call
        success, img, msg = self.service.generate_image("A forest", provider="Stable Diffusion XL")
        
        # Verify
        self.assertTrue(success)
        self.assertEqual(img, expected_image)
        self.assertIn("Stable Diffusion XL", msg)
        mock_client_instance.text_to_image.assert_called_with("A forest", model="stabilityai/stable-diffusion-xl-base-1.0")

    @patch('modules.image_gen.service.InferenceClient')
    @patch('modules.image_gen.service.os.path.exists')
    @patch('modules.image_gen.service.Image.open')
    def test_generate_image_hf_image_to_image(self, mock_img_open, mock_exists, mock_inference_client):
        # Setup Mock
        mock_client_instance = MagicMock()
        mock_inference_client.return_value = mock_client_instance
        
        mock_exists.return_value = True
        mock_exists.return_value = True
        mock_source_img = MagicMock()
        mock_source_img.size = (512, 512)
        mock_img_open.return_value = mock_source_img
        
        expected_result_img = "Result_Image"
        mock_client_instance.image_to_image.return_value = expected_result_img
        
        # Call
        success, img, msg = self.service.generate_image("Make it snowy", provider="Stable Diffusion XL", image_path="/path/to/source.png")
        
        # Verify
        self.assertTrue(success)
        self.assertEqual(img, expected_result_img)
        self.assertIn("modifiée", msg)
        mock_client_instance.image_to_image.assert_called_with(
            image=mock_source_img, 
            prompt="Make it snowy", 
            model="stabilityai/stable-diffusion-xl-base-1.0"
        )



    @patch('modules.image_gen.service.QwenImageEditPlusPipeline')
    @patch('modules.image_gen.service.Image.open')
    @patch('modules.image_gen.service.os.path.exists')
    @patch('modules.image_gen.service.torch')
    def test_generate_image_qwen(self, mock_torch, mock_exists, mock_img_open, mock_pipeline_cls):
        # Setup
        mock_exists.return_value = True
        mock_pipeline = MagicMock()
        mock_pipeline_cls.from_pretrained.return_value = mock_pipeline
        mock_torch.cuda.is_available.return_value = False # CPU test
        
        # Mock Image
        mock_img = MagicMock()
        mock_img.convert.return_value = mock_img # chaining
        mock_img_open.return_value = mock_img
        
        # Mock Output
        mock_output = MagicMock()
        mock_output.images = ["Qwen_Output_Image"]
        mock_pipeline.return_value = mock_output
        
        success, img, msg = self.service.generate_image("Make it pop", provider="Qwen-Image-Edit-2509", image_path="test.png")
        
        self.assertTrue(success)
        self.assertEqual(img, "Qwen_Output_Image")
        self.assertIn("Qwen Local", msg)
        mock_pipeline_cls.from_pretrained.assert_called()

    def test_generate_image_openai_img2img_fail(self):
        # OpenAI provider should fail if image_path is provided (as per current implementation limitation or design)
        success, img, msg = self.service.generate_image("test", provider="OpenAI DALL-E 3", image_path="/some/path.png")
        self.assertFalse(success)
        self.assertIn("ne supporte pas l'édition", msg)

if __name__ == '__main__':
    unittest.main()
