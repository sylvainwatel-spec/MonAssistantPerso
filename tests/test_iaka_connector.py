import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add parent directory to path to import utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.services.llm_service import LLMService as LLMConnectionTester

class TestIAKAConnector(unittest.TestCase):
    @patch('openai.OpenAI')
    def test_iaka_url_construction(self, mock_openai):
        # Setup mock
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Mock Response"))]
        mock_client.chat.completions.create.return_value = mock_response

        # Scenario 1: Root URL (Should append model/v1)
        api_key = "test_key"
        base_url = "https://iaka-api.custom.net"
        expected_full_url_1 = "https://iaka-api.custom.net/mistral-medium/v1"
        LLMConnectionTester.test_provider("IAKA (Interne)", api_key, base_url=base_url, model="mistral-medium")
        mock_openai.assert_called_with(api_key=api_key, base_url=expected_full_url_1)

        # Scenario 2: Full URL (Should NOT append anything)
        full_base_url = "https://iaka-api.custom.net/custom-path/v1"
        LLMConnectionTester.test_provider("IAKA (Interne)", api_key, base_url=full_base_url, model="mistral-medium")
        mock_openai.assert_called_with(api_key=api_key, base_url=full_base_url)

    @patch('openai.OpenAI')
    @patch('core.services.llm_service.logger')
    def test_iaka_url_construction_with_trailing_slash(self, mock_logger, mock_openai):
        # Setup mock
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Mock Response"))]
        mock_client.chat.completions.create.return_value = mock_response
        
        # Test with trailing slash (should be removed)
        base_url = "https://iaka-api.custom.net/"
        expected_full_url = "https://iaka-api.custom.net/mistral-small/v1"
        
        # Execute
        LLMConnectionTester.test_provider("IAKA (Interne)", "k", base_url=base_url)
        
        # Verify
        mock_openai.assert_called_with(api_key="k", base_url=expected_full_url)

if __name__ == '__main__':
    unittest.main()
