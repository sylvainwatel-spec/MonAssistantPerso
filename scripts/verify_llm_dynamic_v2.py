import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.services.llm_service import LLMService

class TestLLMFetching(unittest.TestCase):
    
    @patch('core.services.llm_service.LLMService._fetch_openai_models')
    def test_fetch_openai(self, mock_fetch):
        mock_fetch.return_value = ["gpt-4o", "gpt-3.5-turbo"]
        models = LLMService.fetch_models("OpenAI", "sk-test")
        self.assertEqual(models, ["gpt-4o", "gpt-3.5-turbo"])
        mock_fetch.assert_called_once()  # Ensure it IS called

    @patch('core.services.llm_service.LLMService._fetch_groq_models')
    def test_fetch_groq(self, mock_fetch):
        mock_fetch.return_value = ["llama3-8b"]
        models = LLMService.fetch_models("Groq", "gsk-test")
        self.assertEqual(models, ["llama3-8b"])
        mock_fetch.assert_called_once()
        
    def test_fetch_anthropic_static(self):
        models = LLMService.fetch_models("Anthropic Claude", "sk-ant-test")
        self.assertIn("claude-3-opus-20240229", models)
        
    # Testing the interaction with base_url inside using a mock would be better
    # checking if it handles empty string
    @patch('openai.OpenAI')
    def test_openai_empty_base_url(self, mock_client_class):
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.models.list.return_value.data = []
        
        # Test directly the helper
        LLMService._fetch_openai_models("key", "")
        
        # Verify call args
        mock_client_class.assert_called_with(api_key="key", base_url=None)
        print("✅ OpenAI Client created with base_url=None when input was ''")

if __name__ == '__main__':
    unittest.main()
