import unittest
from unittest.mock import MagicMock, patch
import os
import sys

# Ensure modules can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.doc_analyst.service import DocumentAnalysisService

class TestDocumentAnalysisService(unittest.TestCase):
    def setUp(self):
        self.mock_data_manager = MagicMock()
        self.mock_data_manager.get_settings.return_value = {
            "api_keys": {"OpenAI GPT-4o mini": "sk-test-key"},
            "doc_analyst_provider": "OpenAI GPT-4o mini"
        }
        self.service = DocumentAnalysisService(self.mock_data_manager)

    @patch('os.path.exists')
    @patch('modules.doc_analyst.service.PdfReader')
    def test_extract_text_pdf(self, mock_pdf_reader, mock_exists):
        mock_exists.return_value = True
        
        # Mock PDF content
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Page text"
        mock_reader = MagicMock()
        mock_reader.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader

        success, text = self.service.extract_text("test.pdf")
        
        self.assertTrue(success)
        self.assertIn("Page text", text)

    @patch('os.path.exists')
    def test_extract_text_txt(self, mock_exists):
        mock_exists.return_value = True
        
        # We need to mock open explicitly for the exact file path or generally
        with patch('builtins.open', unittest.mock.mock_open(read_data="File content")):
            success, text = self.service.extract_text("test.txt")
            
            self.assertTrue(success)
            self.assertEqual(text, "File content")

    def test_extract_text_not_found(self):
        with patch('os.path.exists', return_value=False):
            success, msg = self.service.extract_text("missing.pdf")
            self.assertFalse(success)
            self.assertIn("non trouvé", msg)

    @patch('modules.doc_analyst.service.LLMService.generate_response')
    def test_chat_with_document(self, mock_generate):
        mock_generate.return_value = (True, "Analysis result")
        
        history = [{"role": "user", "content": "Hi"}]
        success, response = self.service.chat_with_document("Doc content", "Question", history, "OpenAI GPT-4o mini")
        
        self.assertTrue(success)
        self.assertEqual(response, "Analysis result")
        
        # Verify prompt construction
        args, _ = mock_generate.call_args
        messages = args[2]
        self.assertIn("system", messages[0]['role'])
        self.assertIn("Doc content", messages[0]['content'])

if __name__ == '__main__':
    unittest.main()
