import utils.patch_langchain
from scrapegraphai.graphs import SmartScraperGraph
import os

# Mock API key if not present
if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = "sk-mock-key"
if "ANTHROPIC_API_KEY" not in os.environ:
    os.environ["ANTHROPIC_API_KEY"] = "sk-ant-mock-key"

def test_repro():
    graph_config = {
        "llm": {
            "api_key": "sk-ant-mock-key",
            "model": "claude-3-opus-20240229",
        },
        "verbose": True,
        "headless": True,
    }

    try:
        scraper = SmartScraperGraph(
            prompt="Test prompt",
            source="https://example.com",
            config=graph_config
        )
        print("Graph initialized successfully")
    except Exception as e:
        with open("error.log", "w", encoding="utf-8") as f:
            f.write(f"Caught exception: {e}\n")
            import traceback
            traceback.print_exc(file=f)
        print(f"Caught exception: {e}")

if __name__ == "__main__":
    test_repro()
