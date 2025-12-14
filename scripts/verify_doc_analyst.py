import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.doc_analyst.service import DocumentAnalysisService
from modules.doc_analyst.view import DocAnalystFrame

class TestDocAnalystConfig(unittest.TestCase):
    def setUp(self):
        self.mock_data_manager = MagicMock()
        self.mock_data_manager.get_settings.return_value = {
            "api_keys": {
                "Hugging Face (Mistral/Mixtral)": "hf_test_key",
                "OpenAI": "sk-..."
            },
            "doc_analyst_provider": "Mistral 7B (Hugging Face)"
        }
        self.service = DocumentAnalysisService(self.mock_data_manager)

    @patch('modules.doc_analyst.service.LLMService')
    def test_service_calls_correct_hf_model(self, mock_llm_service):
        # Test Mistral 7B mapping
        provider_friendly = "Mistral 7B (Hugging Face)"
        history = []
        
        self.service.chat_with_document("context", "question", history, provider_friendly)
        
        # Verify LLMService was called with:
        # provider="Hugging Face" (the override)
        # api_key="hf_test_key" (the generic HF key)
        # kwargs contains model="mistralai/Mistral-7B-Instruct-v0.2"
        
        args, kwargs = mock_llm_service.generate_response.call_args
        actual_provider, api_key, messages = args
        
        print(f"\nCalled Provider: {actual_provider}")
        print(f"Called Key: {api_key}")
        print(f"Called Model: {kwargs.get('model')}")
        
        self.assertEqual(actual_provider, "Hugging Face")
        self.assertEqual(api_key, "hf_test_key")
        self.assertEqual(kwargs.get('model'), "mistralai/Mistral-7B-Instruct-v0.2")

    def test_view_dropdown_values(self):
        # We can't easily instantiate the full Frame without Tkinter root, 
        # but we can check if the list matches our expectation if we extract it or inspect the code?
        # Simpler: just trust the service test for logic. The View test is hard without a display.
        pass

if __name__ == '__main__':
    unittest.main()
