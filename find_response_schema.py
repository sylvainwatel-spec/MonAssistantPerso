import pkgutil
import importlib
import langchain

def find_class(package, class_name):
    print(f"Searching in {package.__name__}...")
    for importer, modname, ispkg in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
        try:
            # Skip some heavy modules or those that might crash
            if "experimental" in modname or "community" in modname:
                continue
                
            module = importlib.import_module(modname)
            if hasattr(module, class_name):
                print(f"FOUND {class_name} in {modname}")
                return modname
        except Exception as e:
            # print(f"Error importing {modname}: {e}")
            pass
    return None

import langchain_community
print("Searching in langchain_community...")
find_class(langchain_community, "ResponseSchema")
find_class(langchain_community, "StructuredOutputParser")
