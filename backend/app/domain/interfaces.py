from abc import ABC, abstractmethod
from typing import List, Dict, Any
from .base_models import ModelDefinition

class ProviderPlugin(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """e.g., 'anthropic', 'openai'"""
        pass

    @abstractmethod
    def get_supported_models(self) -> List[ModelDefinition]:
        """Returns the models and their capability profiles for this provider."""
        pass

    @abstractmethod
    def compile_prompt(self, task_spec: Dict[str, Any], model_id: str) -> str:
        """
        The core compiler method. 
        Translates a generalized PromptOS TaskSpecification into 
        the provider's highly optimized specific string/JSON format.
        """
        pass