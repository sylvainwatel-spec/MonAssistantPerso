
import unittest
import os
import pandas as pd
import shutil
import sys
import os
# Add root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.data_viz.services import DataAnalysisService

# Mock DataManager
class MockDataManager:
    def get_settings(self):
        return {
            "chat_provider": "OpenAI GPT-4o mini",
            "api_keys": {},
            "models": {},
            "endpoints": {}
        }

class TestDataViz(unittest.TestCase):
    def setUp(self):
        self.test_csv = "test_data.csv"
        # Create dummy CSV
        df = pd.DataFrame({
            'Name': ['A', 'B', 'C', 'D'],
            'Value': [10, 20, 15, 30],
            'Category': ['X', 'Y', 'X', 'Y']
        })
        df.to_csv(self.test_csv, index=False)
        
        self.service = DataAnalysisService(MockDataManager())
        self.output_pptx = "test_output.pptx"

    def tearDown(self):
        if os.path.exists(self.test_csv):
            os.remove(self.test_csv)
        if os.path.exists(self.output_pptx):
            os.remove(self.output_pptx)

    def test_load_and_stats(self):
        success = self.service.load_file(self.test_csv)
        self.assertTrue(success, "File loading failed")
        self.assertIsNotNone(self.service.df, "DataFrame is None")
        
        stats = self.service.get_basic_stats()
        self.assertIn("Name", stats)
        self.assertIn("Value", stats)
        self.assertIn("4 lignes", stats)

    def test_chart_generation(self):
        self.service.load_file(self.test_csv)
        fig = self.service.generate_chart()
        self.assertIsNotNone(fig, "Chart generation failed")
        import matplotlib.pyplot as plt
        plt.close(fig)

    def test_export(self):
        self.service.load_file(self.test_csv)
        success = self.service.export_to_pptx(self.output_pptx, "AI Analysis Placeholder")
        self.assertTrue(success, "Export failed")
        self.assertTrue(os.path.exists(self.output_pptx), "PPTX file not created")
        self.assertGreater(os.path.getsize(self.output_pptx), 0, "PPTX file is empty")

    def test_analyze_with_provider_override(self):
        self.service.load_file(self.test_csv)
        # We can't easily mock the actual LLM call without more mocking, 
        # but we can ensure the method accepts the argument and tries to use it.
        # Since we don't have a valid key for "IAKA (Interne)" in mock settings, it should fail gracefully 
        # or return a specific error message about missing key if logic is correct.
        
        # Inject a dummy key for IAKA to see if it proceeds to call (which will fail on connection but pass key check)
        self.service.data_manager.get_settings = lambda: {
            "chat_provider": "OpenAI", 
            "api_keys": {"IAKA (Interne)": "dummy_key"},
            "endpoints": {},
            "models": {}
        }
        
        # This will likely return an error string from LLMService, but shouldn't crash
        result = self.service.analyze_with_llm(provider_override="IAKA (Interne)")
        self.assertIsInstance(result, str)
        # It should probably say something about connection error or IAKA error, 
        # confirming it tried to use IAKA.
        self.assertTrue("IAKA" in result or "Erreur" in result)

if __name__ == '__main__':
    unittest.main()
