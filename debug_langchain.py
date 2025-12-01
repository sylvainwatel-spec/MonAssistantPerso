try:
    import langchain.output_parsers
    print("Imported langchain.output_parsers")
    print(dir(langchain.output_parsers))
except ImportError as e:
    print(f"Failed to import langchain.output_parsers: {e}")

try:
    from langchain.output_parsers import ResponseSchema
    print("Found ResponseSchema in langchain.output_parsers")
except ImportError as e:
    print(f"Failed to import ResponseSchema: {e}")

try:
    import langchain_core.output_parsers
    print("Imported langchain_core.output_parsers")
    print(dir(langchain_core.output_parsers))
except ImportError as e:
    print(f"Failed to import langchain_core.output_parsers: {e}")
