from app.domain.interfaces import ProviderPlugin
from app.domain.base_models import ModelDefinition, CapabilityProfile
from app.domain.models.specification import TaskSpecification
from typing import List, Dict

class GPT4Plugin(ProviderPlugin):
    @property
    def provider_name(self) -> str:
        return "openai_gpt4"

    def get_supported_models(self) -> List[ModelDefinition]:
        return [
            ModelDefinition(
                id="gpt-4o",
                name="GPT-4o (Omni)",
                provider="openai_gpt4",
                profile=CapabilityProfile(
                    capabilities=["multimodal", "structured_outputs", "json_mode", "instruction_following"],
                    context_window_tokens=128000,
                    pricing_input_1m=2.50,
                    pricing_output_1m=10.00,
                    latency_tier="fast",
                    strengths=["Exceptional multi-turn instruction following", "Reliable JSON structure adherence", "Broad cross-domain capability"],
                    weaknesses=["Sensitive to conflicting instructions"],
                    recommended_tasks=["Enterprise automation", "Structured data extraction", "RAG chat applications"],
                    avoid_for=[]
                )
            ),
            ModelDefinition(
                id="gpt-4-turbo",
                name="GPT-4 Turbo",
                provider="openai_gpt4",
                profile=CapabilityProfile(
                    capabilities=["long_context", "json_mode", "parallel_function_calling"],
                    context_window_tokens=128000,
                    pricing_input_1m=10.00,
                    pricing_output_1m=30.00,
                    latency_tier="balanced",
                    strengths=["Reliable large-context processing", "Precise function calling"],
                    weaknesses=[],
                    recommended_tasks=["Long document analysis", "API integration workflows"],
                    avoid_for=[]
                )
            )
        ]

    def compile_prompt(self, spec: TaskSpecification, model_id: str) -> List[Dict[str, str]]:
        """
        Formats prompts adhering to OpenAI's official GPT-4 prompting guide strategies:
        - Write clear, specific instructions with distinct markdown headings.
        - Use delimiters (triple quotes) to separate enterprise RAG context.
        - Specify desired output structures and formatting constraints.
        """
        system_content = (
            f"You are operating on OpenAI model '{model_id}'. "
            "You are an expert AI assistant. Follow instructions precisely, pay close attention to enterprise context, "
            "and structure your reasoning clearly before finalizing your output."
        )

        user_parts = []

        # 1. Enterprise RAG Guidelines / Context with Triple Quote Delimiters
        if spec.context_data:
            rules_text = "\n".join([f"- {rule}" for rule in spec.context_data])
            user_parts.append(f"### Enterprise Context & Guidelines\n\"\"\"\n{rules_text}\n\"\"\"")

        # 2. Constraints & Boundaries
        if spec.constraints:
            constraints_text = "\n".join([f"- {c}" for c in spec.constraints])
            user_parts.append(f"### Constraints\n{constraints_text}")

        # 3. Examples (Few-Shot)
        if spec.examples:
            examples_text = ""
            for ex in spec.examples:
                examples_text += f"Input: {ex.get('input')}\nOutput: {ex.get('output')}\n\n"
            user_parts.append(f"### Examples\n{examples_text}")

        # 4. Core Objective
        user_parts.append(f"### Task Objective\n{spec.primary_objective}")

        user_content = "\n\n".join(user_parts)

        return [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content}
        ]