from typing import Dict, List
from app.domain.interfaces import ProviderPlugin
from app.domain.base_models import ModelDefinition

class PluginRegistry:
    def __init__(self):
        self._plugins = {}

    def register(self, plugin):
        # Registers the plugin using its provider_name property
        self._plugins[plugin.provider_name] = plugin

    def get(self, provider_name: str):
        """Retrieves a registered plugin by its provider name."""
        plugin = self._plugins.get(provider_name)
        if not plugin:
            raise ValueError(f"No plugin registered for provider: '{provider_name}'. Available: {list(self._plugins.keys())}")
        return plugin