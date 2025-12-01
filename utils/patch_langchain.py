"""
Patch to fix ScrapeGraphAI compatibility with newer LangChain versions.
Injects 'langchain.prompts' into sys.modules if it's missing, redirecting to 'langchain_core.prompts'.
"""
import sys
import logging

logger = logging.getLogger(__name__)

def apply_patch():
    try:
        import langchain
        import langchain_core.prompts
        import langchain_core.output_parsers
        
        # Check if langchain.prompts exists
        try:
            from langchain import prompts
        except ImportError:
            logger.info("Applying patch: Injecting langchain.prompts")
            sys.modules["langchain.prompts"] = langchain_core.prompts
            
        # Check if langchain.output_parsers exists
        try:
            from langchain import output_parsers
        except ImportError:
            logger.info("Applying patch: Injecting langchain.output_parsers")
            
            # Create a dummy module for output_parsers
            import types
            output_parsers_module = types.ModuleType("langchain.output_parsers")
            
            # Try to populate with langchain_core.output_parsers content
            for name in dir(langchain_core.output_parsers):
                setattr(output_parsers_module, name, getattr(langchain_core.output_parsers, name))
            
            # Add missing classes (Mocks)
            class ResponseSchema:
                def __init__(self, name, description, type="string"):
                    self.name = name
                    self.description = description
                    self.type = type
            
            class StructuredOutputParser:
                def __init__(self, response_schemas):
                    self.response_schemas = response_schemas
                
                @classmethod
                def from_response_schemas(cls, response_schemas):
                    return cls(response_schemas)
                
                def get_format_instructions(self):
                    return ""
                
                def parse(self, text):
                    return text
            
            output_parsers_module.ResponseSchema = ResponseSchema
            output_parsers_module.StructuredOutputParser = StructuredOutputParser
            
            sys.modules["langchain.output_parsers"] = output_parsers_module
            
    except ImportError as e:
        logger.warning(f"Could not apply langchain patch: {e}")

# Apply patch immediately on import
apply_patch()
