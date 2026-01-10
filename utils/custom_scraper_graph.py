import logging
from typing import Optional, Type
from pydantic import BaseModel

# Initialize logger
logger = logging.getLogger(__name__)

class CustomSmartScraperGraph:
    """
    Custom version of SmartScraperGraph that correctly passes the 'headless' configuration
    to the FetchNode.
    
    This class uses lazy loading to avoid importing scrapegraphai at module level.
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize by lazy loading SmartScraperGraph and delegating to it."""
        # Lazy import scrapegraphai only when needed
        from scrapegraphai.graphs import SmartScraperGraph
        
        # Create a dynamic class that inherits from SmartScraperGraph
        class _CustomSmartScraperGraphImpl(SmartScraperGraph):
            """Internal implementation that extends SmartScraperGraph."""
            
            def _create_graph(self):
                """
                Creates the graph of nodes representing the workflow for web scraping.
                """
                # Import nodes only when creating the graph
                from scrapegraphai.nodes import (
                    ConditionalNode,
                    FetchNode,
                    GenerateAnswerNode,
                    ParseNode,
                    ReasoningNode,
                )
                from scrapegraphai.graphs.base_graph import BaseGraph
                from scrapegraphai.prompts import REGEN_ADDITIONAL_INFO
                
                if self.llm_model == "scrapegraphai/smart-scraper":
                    try:
                        from scrapegraph_py import Client
                        from scrapegraph_py.logger import sgai_logger
                    except ImportError:
                        raise ImportError(
                            "scrapegraph_py is not installed. Please install it using 'pip install scrapegraph-py'."
                        )

                    sgai_logger.set_logging(level="INFO")

                    # Initialize the client with explicit API key
                    sgai_client = Client(api_key=self.config.get("api_key"))

                    # SmartScraper request
                    response = sgai_client.smartscraper(
                        website_url=self.source,
                        user_prompt=self.prompt,
                    )

                    # Use logging instead of print for better production practices
                    if 'request_id' in response and 'result' in response:
                        logger.info(f"Request ID: {response['request_id']}")
                        logger.info(f"Result: {response['result']}")
                    else:
                        logger.warning("Missing expected keys in response.")

                    sgai_client.close()

                    return response

                # FIX: Pass headless config to FetchNode
                fetch_node = FetchNode(
                    input="url | local_dir",
                    output=["doc"],
                    node_config={
                        "llm_model": self.llm_model,
                        "force": self.config.get("force", False),
                        "cut": self.config.get("cut", True),
                        "loader_kwargs": self.config.get("loader_kwargs", {}),
                        "browser_base": self.config.get("browser_base"),
                        "scrape_do": self.config.get("scrape_do"),
                        "storage_state": self.config.get("storage_state"),
                        "headless": self.config.get("headless", True), # Added this line
                    },
                )
                
                parse_node = ParseNode(
                    input="doc",
                    output=["parsed_doc"],
                    node_config={"llm_model": self.llm_model, "chunk_size": self.model_token},
                )

                generate_answer_node = GenerateAnswerNode(
                    input="user_prompt & (relevant_chunks | parsed_doc | doc)",
                    output=["answer"],
                    node_config={
                        "llm_model": self.llm_model,
                        "additional_info": self.config.get("additional_info"),
                        "schema": self.schema,
                    },
                )

                cond_node = None
                regen_node = None
                if self.config.get("reattempt") is True:
                    cond_node = ConditionalNode(
                        input="answer",
                        output=["answer"],
                        node_name="ConditionalNode",
                        node_config={
                            "key_name": "answer",
                            "condition": 'not answer or answer=="NA"',
                        },
                    )
                    regen_node = GenerateAnswerNode(
                        input="user_prompt & answer",
                        output=["answer"],
                        node_config={
                            "llm_model": self.llm_model,
                            "additional_info": REGEN_ADDITIONAL_INFO,
                            "schema": self.schema,
                        },
                    )

                if self.config.get("html_mode") is False:
                    parse_node = ParseNode(
                        input="doc",
                        output=["parsed_doc"],
                        node_config={
                            "llm_model": self.llm_model,
                            "chunk_size": self.model_token,
                        },
                    )

                reasoning_node = None
                if self.config.get("reasoning"):
                    reasoning_node = ReasoningNode(
                        input="user_prompt & (relevant_chunks | parsed_doc | doc)",
                        output=["answer"],
                        node_config={
                            "llm_model": self.llm_model,
                            "additional_info": self.config.get("additional_info"),
                            "schema": self.schema,
                        },
                    )

                # Define the graph variation configurations
                # (html_mode, reasoning, reattempt)
                graph_variation_config = {
                    (False, True, False): {
                        "nodes": [fetch_node, parse_node, reasoning_node, generate_answer_node],
                        "edges": [
                            (fetch_node, parse_node),
                            (parse_node, reasoning_node),
                            (reasoning_node, generate_answer_node),
                        ],
                    },
                    (True, True, False): {
                        "nodes": [fetch_node, reasoning_node, generate_answer_node],
                        "edges": [
                            (fetch_node, reasoning_node),
                            (reasoning_node, generate_answer_node),
                        ],
                    },
                    (True, False, False): {
                        "nodes": [fetch_node, generate_answer_node],
                        "edges": [(fetch_node, generate_answer_node)],
                    },
                    (False, False, False): {
                        "nodes": [fetch_node, parse_node, generate_answer_node],
                        "edges": [(fetch_node, parse_node), (parse_node, generate_answer_node)],
                    },
                    (False, True, True): {
                        "nodes": [
                            fetch_node,
                            parse_node,
                            reasoning_node,
                            generate_answer_node,
                            cond_node,
                            regen_node,
                        ],
                        "edges": [
                            (fetch_node, parse_node),
                            (parse_node, reasoning_node),
                            (reasoning_node, generate_answer_node),
                            (generate_answer_node, cond_node),
                            (cond_node, regen_node),
                            (cond_node, None),
                        ],
                    },
                    (True, True, True): {
                        "nodes": [
                            fetch_node,
                            reasoning_node,
                            generate_answer_node,
                            cond_node,
                            regen_node,
                        ],
                        "edges": [
                            (fetch_node, reasoning_node),
                            (reasoning_node, generate_answer_node),
                            (generate_answer_node, cond_node),
                            (cond_node, regen_node),
                            (cond_node, None),
                        ],
                    },
                    (True, False, True): {
                        "nodes": [fetch_node, generate_answer_node, cond_node, regen_node],
                        "edges": [
                            (fetch_node, generate_answer_node),
                            (generate_answer_node, cond_node),
                            (cond_node, regen_node),
                            (cond_node, None),
                        ],
                    },
                    (False, False, True): {
                        "nodes": [
                            fetch_node,
                            parse_node,
                            generate_answer_node,
                            cond_node,
                            regen_node,
                        ],
                        "edges": [
                            (fetch_node, parse_node),
                            (parse_node, generate_answer_node),
                            (generate_answer_node, cond_node),
                            (cond_node, regen_node),
                            (cond_node, None),
                        ],
                    },
                }

                # Get the current conditions
                html_mode = self.config.get("html_mode", False)
                reasoning = self.config.get("reasoning", False)
                reattempt = self.config.get("reattempt", False)

                # Retrieve the appropriate graph configuration
                config = graph_variation_config.get((html_mode, reasoning, reattempt))

                if config:
                    return BaseGraph(
                        nodes=config["nodes"],
                        edges=config["edges"],
                        entry_point=fetch_node,
                        graph_name=self.__class__.__name__,
                    )

                # Default return if no conditions match
                return BaseGraph(
                    nodes=[fetch_node, parse_node, generate_answer_node],
                    edges=[(fetch_node, parse_node), (parse_node, generate_answer_node)],
                    entry_point=fetch_node,
                    graph_name=self.__class__.__name__,
                )
        
        # Store the implementation instance
        self._impl = _CustomSmartScraperGraphImpl(*args, **kwargs)
    
    def __getattr__(self, name):
        """Delegate all attribute access to the implementation."""
        return getattr(self._impl, name)
    
    def run(self):
        """Run the scraper graph."""
        return self._impl.run()
