import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import utils.patch_langchain
from scrapegraphai.graphs import SmartScraperGraph
print("Import successful!")
