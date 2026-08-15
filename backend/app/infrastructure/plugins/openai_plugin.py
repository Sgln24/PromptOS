from app.domain.interfaces import ProviderPlugin
from app.domain.base_models import ModelDefinition, CapabilityProfile
from app.domain.models.specification import TaskSpecification
from typing import List, Dict

class OpenAIPlugin(ProviderPlugin):
    @property
    def provider_name(self) -> str:
        return "openai"

    def get_supported_models(self) -> List[ModelDefinition]:
        return [
            ModelDefinition(
                id="gpt-4o",
                name="GPT-4o",
                provider="openai",
                profile=CapabilityProfile(
                    capabilities=["multimodal", "fast_reasoning", "structured_outputs", "json_mode"],
                    context_window_tokens=128000,
                    pricing_input_1m=2.50,
                    pricing_output_1m=10.00,
                    latency_tier="fast",
                    strengths=["Structured JSON generation", "Rapid instruction-following", "Broad multi-domain knowledge"],
                    weaknesses=["Less tolerant of messy unformatted context than Claude"],
                    recommended_tasks=["API integration", "Structured data extraction", "General enterprise chat"],
                    avoid_for=[]
                )
            ),
            ModelDefinition(
                id="o3-mini",
                name="O3-mini (Reasoning)",
                provider="openai",
                profile=CapabilityProfile(
                    capabilities=["advanced_reasoning", "coding", "math", "logic"],
                    context_window_tokens=200000,
                    pricing_input_1m=1.10,
                    pricing_output_1m=4.40,
                    latency_tier="slow",
                    strengths=["Deep mathematical and logical reasoning", "Cost-effective reasoning model"],
                    weaknesses=["Higher latency due to thinking time"],
                    recommended_tasks=["Complex coding logic", "Algorithmic problem solving"],
                    avoid_for=["Simple fast conversational tasks"]
                )
            )
        ]

    def compile_prompt(self, spec: TaskSpecification, model_id: str) -> List[Dict[str, str]]:
        """
        Formats prompts adhering to OpenAI developer best practices:
        - Uses Markdown headings and clean structural separation.
        - Employs triple-quote delimiters for RAG context and guidelines.
        - Clearly sets boundaries and objectives.
        """
        system_prompt = (
            f"You are operating on OpenAI model '{model_id}'. "
            "You are an expert AI assistant and prompt engineer. "
            "Follow the user's instructions carefully, adhering to the enterprise context and boundaries provided."
        )

        user_content_parts = []

        # 1. Enterprise Context / RAG Guidelines (Delimited with triple quotes)
        if spec.context_data:
            rules_text = "\n".join([f"- {rule}" for rule in spec.context_data])
            user_content_parts.append(f"### Enterprise Context & Guidelines\n\"\"\"\n{rules_text}\n\"\"\"")

        # 2. Boundaries & Constraints
        if spec.constraints:
            constraints_text = "\n".join([f"- {c}" for c in spec.constraints])
            user_content_parts.append(f"### Boundaries & Constraints\n{constraints_text}")

        # 3. Examples
        if spec.examples:
            examples_text = ""
            for ex in spec.examples:
                examples_text += f"**Input:** {ex.get('input')}\n**Output:** {ex.get('output')}\n\n"
            user_content_parts.append(f"### Examples\n{examples_text}")

        # 4. Core Objective
        user_content_parts.append(f"### Objective\n{spec.primary_objective}")

        final_user_message = "\n\n".join(user_content_parts)

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": final_user_message}
        ]