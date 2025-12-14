import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock pypdf before importing service
sys.modules['pypdf'] = MagicMock()

from modules.doc_analyst.service import DocumentAnalysisService

class TestDocumentAnalysisService(unittest.TestCase):
    def setUp(self):
        self.mock_data_manager = MagicMock()
        self.service = DocumentAnalysisService(self.mock_data_manager)

    @patch('modules.doc_analyst.service.os.path.exists')
    @patch('modules.doc_analyst.service.PdfReader')
    def test_extract_text_pdf(self, mock_pdf_reader, mock_exists):
        # Setup Mocks
        mock_exists.return_value = True
        
        mock_reader_instance = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Page Content"
        mock_reader_instance.pages = [mock_page, mock_page]
        mock_pdf_reader.return_value = mock_reader_instance
        
        # Execute
        success, text = self.service.extract_text("test.pdf")
        
        # Verify
        self.assertTrue(success)
        self.assertEqual(text, "Page Content\nPage Content\n")
        
    @patch('modules.doc_analyst.service.LLMService.generate_response')
    def test_chat_with_document_openai(self, mock_generate):
        # Setup Mocks
        self.mock_data_manager.get_settings.return_value = {
            "api_keys": {"OpenAI GPT-4o mini": "sk-test-key"},
            "endpoints": {},
            "models": {}
        }
        mock_generate.return_value = (True, "Analysis Result")
        
        # Execute
        context = "This is the document content."
        question = "What is this?"
        history = []
        provider = "OpenAI GPT-4o mini"
        
        success, response = self.service.chat_with_document(context, question, history, provider)
        
        # Verify
        self.assertTrue(success)
        self.assertEqual(response, "Analysis Result")
        
        # Check args passed to generate_response
        args, kwargs = mock_generate.call_args
        self.assertEqual(args[0], provider)
        self.assertEqual(args[1], "sk-test-key")
        self.assertEqual(len(args[2]), 2) # System + User (History empty)
        self.assertIn("content.", args[2][0]['content']) # System prompt contains context
        self.assertEqual(args[2][1]['content'], question)

    @patch('modules.doc_analyst.service.LLMService.generate_response')
    def test_chat_with_document_iaka(self, mock_generate):
        # Setup Mocks
        self.mock_data_manager.get_settings.return_value = {
            "api_keys": {"IAKA": "sk-iaka"},
            "endpoints": {"IAKA": "http://localhost:8080/v1"},
            "models": {"IAKA": "mistral-tiny"}
        }
        mock_generate.return_value = (True, "IAKA Response")
        
        # Execute
        success, response = self.service.chat_with_document("Ctx", "Q", [], "IAKA")
        
        self.assertTrue(success)
        # Check specific kwargs for IAKA
        args, kwargs = mock_generate.call_args
        self.assertEqual(kwargs.get('base_url'), "http://localhost:8080/v1")
        self.assertEqual(kwargs.get('model'), "mistral-tiny")

if __name__ == '__main__':
    unittest.main()
