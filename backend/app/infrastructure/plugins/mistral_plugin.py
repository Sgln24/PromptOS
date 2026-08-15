from app.domain.interfaces import ProviderPlugin
from app.domain.base_models import ModelDefinition, CapabilityProfile
from app.domain.models.specification import TaskSpecification
from typing import List, Dict

class MistralPlugin(ProviderPlugin):
    @property
    def provider_name(self) -> str:
        return "mistral"

    def get_supported_models(self) -> List[ModelDefinition]:
        return [
            ModelDefinition(
                id="mistral-large-latest",
                name="Mistral Large",
                provider="mistral",
                profile=CapabilityProfile(
                    capabilities=["reasoning", "multilingual", "coding", "json_mode"],
                    context_window_tokens=128000,
                    pricing_input_1m=2.0,
                    pricing_output_1m=6.0,
                    latency_tier="balanced",
                    strengths=["Top-tier reasoning and code generation", "Fluent multilingual support", "Exceptional structured JSON output"],
                    weaknesses=[],
                    recommended_tasks=["Complex enterprise reasoning", "Multilingual translation and summarization", "JSON extraction"],
                    avoid_for=[]
                )
            ),
            ModelDefinition(
                id="mistral-small-latest",
                name="Mistral Small",
                provider="mistral",
                profile=CapabilityProfile(
                    capabilities=["speed", "cost_efficiency", "classification", "summarization"],
                    context_window_tokens=128000,
                    pricing_input_1m=0.2,
                    pricing_output_1m=0.6,
                    latency_tier="fast",
                    strengths=["High throughput and low latency", "Cost-efficient high-volume processing"],
                    weaknesses=["Lower reasoning depth than Mistral Large"],
                    recommended_tasks=["Fast text extraction", "High-volume classification", "Standard summarization"],
                    avoid_for=["Extremely complex mathematical logic"]
                )
            ),
            ModelDefinition(
                id="mistral-7b-instruct",
                name="Mistral 7B Instruct",
                provider="mistral",
                profile=CapabilityProfile(
                    capabilities=["local_efficient", "open_weights", "instruction_following"],
                    context_window_tokens=32768,
                    pricing_input_1m=0.0,
                    pricing_output_1m=0.0,
                    latency_tier="fast",
                    strengths=["Outperforms larger legacy models", "Ideal for local fine-tuning and deployment"],
                    weaknesses=["Smaller parameter ceiling for deep encyclopedic facts"],
                    recommended_tasks=["Local RAG pipelines", "Lightweight chat and generation tasks"],
                    avoid_for=[]
                )
            )
        ]

    def compile_prompt(self, spec: TaskSpecification, model_id: str) -> List[Dict[str, str]]:
        """
        Formats prompts adhering to Mistral AI official prompting guidelines:
        - Lead with a clear role-and-task purpose.
        - Structure prompts hierarchically using clear markdown sections (Context, Constraints, Examples, Task Objective).
        - Avoid subjective descriptions; use explicit guidelines.
        """
        system_content = (
            f"You are operating on Mistral model '{model_id}'. "
            "You are an expert assistant. Your task is to execute the user's objective precisely, following all hierarchical markdown sections and constraints."
        )

        user_parts = []

        # 1. Context & Background (Enterprise RAG Guidelines)
        if spec.context_data:
            rules_text = "\n".join([f"- {rule}" for rule in spec.context_data])
            user_parts.append(f"## Context\n{rules_text}")

        # 2. Constraints & Rules
        if spec.constraints:
            constraints_text = "\n".join([f"- {c}" for c in spec.constraints])
            user_parts.append(f"## Constraints\n{constraints_text}")

        # 3. Examples (Few-Shot Formatting)
        if spec.examples:
            examples_text = ""
            for ex in spec.examples:
                examples_text += f"Input: {ex.get('input')}\nOutput: {ex.get('output')}\n\n"
            user_parts.append(f"## Examples\n{examples_text}")

        # 4. Task Objective & Execution Steps
        user_parts.append(f"## Task Objective\n{spec.primary_objective}")

        user_content = "\n\n".join(user_parts)

        return [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content}
        ]