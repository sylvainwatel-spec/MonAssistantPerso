import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add parent directory to path to import utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.llm_connector import LLMConnectionTester

class TestIAKAConnector(unittest.TestCase):
    @patch('openai.OpenAI')
    def test_iaka_url_construction(self, mock_openai):
        # Setup mock
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Mock Response"))]
        mock_client.chat.completions.create.return_value = mock_response

        # Test inputs
        api_key = "test_key"
        base_url = "https://iaka-api.custom.net"
        expected_full_url = "https://iaka-api.custom.net/mistral-small/v1"
        
        # Execute
        success, message = LLMConnectionTester.test_provider("IAKA (Interne)", api_key, base_url=base_url)
        
        # Verify
        self.assertTrue(success)
        mock_openai.assert_called_with(api_key=api_key, base_url=expected_full_url)
        mock_client.chat.completions.create.assert_called_with(
            model="mistral-small",
            messages=[{"role": "user", "content": "Hello"}],
            temperature=0.1,
            top_p=1,
            max_tokens=5,
            stream=False
        )
        self.assertIn("Connexion réussie à IAKA", message)
        self.assertIn(expected_full_url, message)

    @patch('openai.OpenAI')
    def test_iaka_url_construction_with_trailing_slash(self, mock_openai):
        # Setup mock
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Mock Response"))]
        mock_client.chat.completions.create.return_value = mock_response
        
        # Test with trailing slash
        base_url = "https://iaka-api.custom.net/"
        expected_full_url = "https://iaka-api.custom.net/mistral-small/v1"
        
        # Execute
        LLMConnectionTester.test_provider("IAKA (Interne)", "k", base_url=base_url)
        
        # Verify
        mock_openai.assert_called_with(api_key="k", base_url=expected_full_url)

if __name__ == '__main__':
    unittest.main()
