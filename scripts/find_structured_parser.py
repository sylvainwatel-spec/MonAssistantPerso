import sys

try:
    from langchain.output_parsers import StructuredOutputParser
    print("Found in langchain.output_parsers")
except ImportError:
    print("Not in langchain.output_parsers")

try:
    from langchain_core.output_parsers import StructuredOutputParser
    print("Found in langchain_core.output_parsers")
except ImportError:
    print("Not in langchain_core.output_parsers")

# Try to find it in sys.modules or walk packages?
# Let's try to import langchain and inspect
import langchain
print(f"Langchain version: {langchain.__version__}")
# print(dir(langchain))
