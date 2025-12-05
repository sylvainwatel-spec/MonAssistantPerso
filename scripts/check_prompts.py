try:
    from langchain_core.prompts import PromptTemplate
    print("Found PromptTemplate in langchain_core.prompts")
except ImportError:
    print("PromptTemplate NOT found in langchain_core.prompts")
