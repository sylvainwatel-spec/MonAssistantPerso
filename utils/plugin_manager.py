# Plugin manager for dynamic page registration

class PluginManager:
    """Simple registry for page plugins.
    Allows decoupling the core App from concrete page classes.
    """

    def __init__(self):
        self._pages = {}

    def register(self, name: str, cls):
        """Register a page class under a given name.
        Args:
            name: Identifier used to retrieve the page.
            cls: The class (subclass of ctk.CTkFrame) to register.
        """
        self._pages[name] = cls

    def get(self, name: str):
        """Retrieve a registered page class by name.
        Returns None if not found.
        """
        return self._pages.get(name)

# Global singleton instance used throughout the project
manager = PluginManager()
