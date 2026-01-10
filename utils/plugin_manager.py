# Plugin manager for dynamic page registration

class PluginManager:
    """Simple registry for page plugins.
    Allows decoupling the core App from concrete page classes.
    Supports lazy loading of page classes to improve startup time.
    """

    def __init__(self):
        self._pages = {}
        self._lazy_loaders = {}

    def register(self, name: str, cls_or_loader):
        """Register a page class or lazy loader under a given name.
        Args:
            name: Identifier used to retrieve the page.
            cls_or_loader: Either a class (subclass of ctk.CTkFrame) or a callable
                          that returns the class when called (for lazy loading).
        """
        if callable(cls_or_loader) and not isinstance(cls_or_loader, type):
            # It's a loader function
            self._lazy_loaders[name] = cls_or_loader
        else:
            # It's a class
            self._pages[name] = cls_or_loader

    def get(self, name: str):
        """Retrieve a registered page class by name.
        If the page was registered with a lazy loader, it will be loaded on first access.
        Returns None if not found.
        """
        # Check if already loaded
        if name in self._pages:
            return self._pages[name]
        
        # Check if there's a lazy loader
        if name in self._lazy_loaders:
            loader = self._lazy_loaders[name]
            cls = loader()
            # Cache the loaded class
            self._pages[name] = cls
            # Remove the loader to free memory
            del self._lazy_loaders[name]
            return cls
        
        return None

# Global singleton instance used throughout the project
manager = PluginManager()
