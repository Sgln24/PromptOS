from app.domain.interfaces import ProviderPlugin
from app.domain.base_models import ModelDefinition, CapabilityProfile
from app.domain.models.specification import TaskSpecification
from typing import List, Dict

class OpenRouterPlugin(ProviderPlugin):
    @property
    def provider_name(self) -> str:
        return "openrouter"

    def get_supported_models(self) -> List[ModelDefinition]:
        return [
            ModelDefinition(
                id="openrouter/anthropic/claude-3.5-sonnet", # LiteLLM syntax for OpenRouter
                name="Claude 3.5 Sonnet (Cloud)",
                provider="openrouter",
                profile=CapabilityProfile(
                    capabilities=["coding", "vision", "complex_reasoning"],
                    context_window_tokens=200000,
                    pricing_input_1m=3.0,
                    pricing_output_1m=15.0,
                    latency_tier="low",
                    strengths=["Top-tier coding capabilities"],
                    weaknesses=["Requires cloud data egress"],
                    recommended_tasks=["Complex Architecture", "Refactoring"],
                    avoid_for=["Strict local privacy requirements"]
                )
            )
        ]

    def compile_prompt(self, spec: TaskSpecification, model_id: str) -> List[Dict[str, str]]:
        # Standard Message Array format
        messages = [{"role": "system", "content": spec.role_persona or "You are a helpful AI."}]
        messages.append({"role": "user", "content": spec.primary_objective})
        return messages