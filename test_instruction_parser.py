import unittest
from utils.instruction_parser import InstructionParser

class TestInstructionParser(unittest.TestCase):
    def setUp(self):
        self.parser = InstructionParser()

    def test_parse_simple_search(self):
        text = """
SEARCH_INPUT: #search-bar
SEARCH_BUTTON: #submit-btn
"""
        result = self.parser.parse(text)
        self.assertEqual(result['search_input'], '#search-bar')
        self.assertEqual(result['search_button'], '#submit-btn')

    def test_parse_with_actions(self):
        text = """
SEARCH_INPUT: input[name="q"]
BEFORE_SEARCH:
  - CLICK: #cookie-accept
  - WAIT: 2s
"""
        result = self.parser.parse(text)
        self.assertEqual(result['search_input'], 'input[name="q"]')
        self.assertEqual(len(result['before_search']), 2)
        self.assertEqual(result['before_search'][0]['type'], 'click')
        self.assertEqual(result['before_search'][0]['selector'], '#cookie-accept')
        self.assertEqual(result['before_search'][1]['type'], 'wait')
        self.assertEqual(result['before_search'][1]['duration'], 2000)

    def test_parse_extract(self):
        text = """
EXTRACT:
  - title: h1.title
  - price: .price-tag
"""
        result = self.parser.parse(text)
        self.assertIn('extract', result)
        self.assertEqual(result['extract']['title'], 'h1.title')
        self.assertEqual(result['extract']['price'], '.price-tag')

    def test_validate_valid(self):
        data = {
            'search_input': '#search',
            'before_search': [{'type': 'wait', 'duration': 1000}]
        }
        is_valid, errors = self.parser.validate(data)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_validate_invalid(self):
        data = {
            'search_input': 123, # Invalid type
            'before_search': [{'type': 'click'}] # Missing selector
        }
        is_valid, errors = self.parser.validate(data)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)

if __name__ == '__main__':
    unittest.main()
