from app.domain.interfaces import ProviderPlugin
from app.domain.base_models import ModelDefinition, CapabilityProfile
from app.domain.models.specification import TaskSpecification
from typing import List, Dict

class GemmaPlugin(ProviderPlugin):
    @property
    def provider_name(self) -> str:
        return "google"

    def get_supported_models(self) -> List[ModelDefinition]:
        return [
            ModelDefinition(
                id="google/gemma-2-9b-it",
                name="Gemma 2 9B Instruct",
                provider="google",
                profile=CapabilityProfile(
                    capabilities=["coding", "instruction_following", "fast_reasoning", "local_efficient"],
                    context_window_tokens=8192,
                    pricing_input_1m=0.20,
                    pricing_output_1m=0.20,
                    latency_tier="fast",
                    strengths=["High performance for parameter size", "Strong code and math capabilities"],
                    weaknesses=["No native system role (requires embedded instructions)"],
                    recommended_tasks=["Local open-weights deployment", "Efficient text generation", "Specialized coding tasks"],
                    avoid_for=[]
                )
            ),
            ModelDefinition(
                id="google/gemma-2-27b-it",
                name="Gemma 2 27B Instruct",
                provider="google",
                profile=CapabilityProfile(
                    capabilities=["deep_reasoning", "coding", "complex_logic"],
                    context_window_tokens=8192,
                    pricing_input_1m=0.80,
                    pricing_output_1m=0.80,
                    latency_tier="balanced",
                    strengths=["Superior reasoning benchmarks", "Dense open weights performance"],
                    weaknesses=["Higher compute requirement than smaller variants"],
                    recommended_tasks=["Advanced open-weights reasoning", "Complex enterprise instructions"],
                    avoid_for=[]
                )
            )
        ]

    def compile_prompt(self, spec: TaskSpecification, model_id: str) -> List[Dict[str, str]]:
        """
        Formats prompts adhering to Google's Gemma formatting guidelines:
        - Gemma IT models do not support a separate system role.
        - System guidelines, enterprise context, and constraints are embedded directly into the user turn.
        """
        user_parts = []

        # 1. Embedded System-Level Instructions (since Gemma IT lacks a system role)
        system_intro = (
            f"You are operating on Google Gemma model '{model_id}'. "
            "Follow all instructions precisely, adopting a professional and expert tone."
        )
        user_parts.append(system_intro)

        # 2. Enterprise RAG Guidelines / Context
        if spec.context_data:
            rules_text = "\n".join([f"- {rule}" for rule in spec.context_data])
            user_parts.append(f"Enterprise Guidelines & Context:\n{rules_text}")

        # 3. Constraints
        if spec.constraints:
            constraints_text = "\n".join([f"- {c}" for c in spec.constraints])
            user_parts.append(f"Constraints:\n{constraints_text}")

        # 4. Examples
        if spec.examples:
            examples_text = ""
            for ex in spec.examples:
                examples_text += f"Input: {ex.get('input')}\nOutput: {ex.get('output')}\n\n"
            user_parts.append(f"Examples:\n{examples_text}")

        # 5. Core Objective
        user_parts.append(f"Task Objective:\n{spec.primary_objective}")

        final_user_content = "\n\n".join(user_parts)

        # Gemma IT models use only user and model roles
        return [
            {"role": "user", "content": final_user_content}
        ]