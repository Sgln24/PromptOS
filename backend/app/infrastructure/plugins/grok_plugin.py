from app.domain.interfaces import ProviderPlugin
from app.domain.base_models import ModelDefinition, CapabilityProfile
from app.domain.models.specification import TaskSpecification
from typing import List, Dict

class GrokPlugin(ProviderPlugin):
    @property
    def provider_name(self) -> str:
        return "xai"

    def get_supported_models(self) -> List[ModelDefinition]:
        return [
            ModelDefinition(
                id="grok-1",
                name="Grok-1 (314B MoE)",
                provider="xai",
                profile=CapabilityProfile(
                    capabilities=["reasoning", "coding", "open_weights", "moe_architecture"],
                    context_window_tokens=8192,
                    pricing_input_1m=0.0,  # Open weights local/self-hosted or API variant
                    pricing_output_1m=0.0,
                    latency_tier="balanced",
                    strengths=["Strong Mixture-of-Experts reasoning", "Apache 2.0 open release lineage", "Unfiltered analytical depth"],
                    weaknesses=["Requires structured framing for complex multi-step tasks"],
                    recommended_tasks=["Open-weights reasoning", "Enterprise RAG workflows", "Coding logic tasks"],
                    avoid_for=[]
                )
            )
        ]

    def compile_prompt(self, spec: TaskSpecification, model_id: str) -> List[Dict[str, str]]:
        """
        Formats prompts adhering to xAI Grok prompting guidelines:
        - Utilizes a structured Context -> Task -> Constraint layout.
        - Uses clear markdown sections to isolate RAG rules and parameters.
        """
        system_content = (
            f"You are operating on xAI model '{model_id}'. "
            "Provide direct, clear, and logically sound answers while adhering strictly to all enterprise guidelines and constraints."
        )

        user_parts = []

        # 1. Enterprise RAG Context / Reference Guidelines
        if spec.context_data:
            rules_text = "\n".join([f"- {rule}" for rule in spec.context_data])
            user_parts.append(f"### Context & Background\n{rules_text}")

        # 2. Constraints & Boundaries
        if spec.constraints:
            constraints_text = "\n".join([f"- {c}" for c in spec.constraints])
            user_parts.append(f"### Constraints & Rules\n{constraints_text}")

        # 3. Examples (Few-Shot)
        if spec.examples:
            examples_text = ""
            for ex in spec.examples:
                examples_text += f"Input: {ex.get('input')}\nOutput: {ex.get('output')}\n\n"
            user_parts.append(f"### Examples\n{examples_text}")

        # 4. Core Objective / Task
        user_parts.append(f"### Task Objective\n{spec.primary_objective}")

        user_content = "\n\n".join(user_parts)

        return [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content}
        ]