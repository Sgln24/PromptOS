from app.domain.interfaces import ProviderPlugin
from app.domain.base_models import ModelDefinition, CapabilityProfile
from app.domain.models.specification import TaskSpecification
from typing import List, Dict

class LlamaPlugin(ProviderPlugin):
    @property
    def provider_name(self) -> str:
        return "meta"

    def get_supported_models(self) -> List[ModelDefinition]:
        return [
            ModelDefinition(
                id="meta/llama-3.3-70b-instruct",
                name="Llama 3.3 70B Instruct",
                provider="meta",
                profile=CapabilityProfile(
                    capabilities=["multilingual", "coding", "reasoning", "long_context"],
                    context_window_tokens=128000,
                    pricing_input_1m=0.70,
                    pricing_output_1m=0.90,
                    latency_tier="balanced",
                    strengths=["Open-weights flagship reasoning", "Strong instruction following", "Multilingual depth"],
                    weaknesses=["Requires explicit instruction structure"],
                    recommended_tasks=["General enterprise text generation", "Coding assistance", "Local/Cloud RAG"],
                    avoid_for=[]
                )
            ),
            ModelDefinition(
                id="codellama/code-llama-70b-instruct",
                name="Code Llama 70B Instruct",
                provider="meta",
                profile=CapabilityProfile(
                    capabilities=["code_generation", "debugging", "unit_testing", "infilling"],
                    context_window_tokens=100000,
                    pricing_input_1m=0.90,
                    pricing_output_1m=0.90,
                    latency_tier="balanced",
                    strengths=["Specialized code understanding", "Native instruction tagging"],
                    weaknesses=["Less optimized for general creative marketing copy"],
                    recommended_tasks=["Code review", "Test generation", "Technical refactoring"],
                    avoid_for=[]
                )
            )
        ]

    def compile_prompt(self, spec: TaskSpecification, model_id: str) -> List[Dict[str, str]]:
        """
        Formats prompts adhering to Meta's Llama and Code Llama instruct guidelines:
        - Uses official <<SYS>> wrapper blocks for system instructions.
        - Packages enterprise context, constraints, and objectives inside [INST] tags.
        """
        system_content = (
            f"You are operating on Meta model '{model_id}'. "
            "You are a precise, highly capable AI assistant and programmer. "
            "Follow all instructions and constraints strictly."
        )

        user_parts = []
        
        # 1. Enterprise RAG Guidelines
        if spec.context_data:
            rules_text = "\n".join([f"- {rule}" for rule in spec.context_data])
            user_parts.append(f"Enterprise Context & Guidelines:\n{rules_text}")

        # 2. Constraints
        if spec.constraints:
            constraints_text = "\n".join([f"- {c}" for c in spec.constraints])
            user_parts.append(f"Constraints:\n{constraints_text}")

        # 3. Examples
        if spec.examples:
            examples_text = ""
            for ex in spec.examples:
                examples_text += f"Input: {ex.get('input')}\nOutput: {ex.get('output')}\n\n"
            user_parts.append(f"Examples:\n{examples_text}")

        # 4. Core Objective
        user_parts.append(f"Task Objective:\n{spec.primary_objective}")

        user_content = "\n\n".join(user_parts)

        # Formatted using Llama's native instruct boundaries
        return [
            {"role": "system", "content": f"<<SYS>>\n{system_content}\n<</SYS>>"},
            {"role": "user", "content": f"[INST]\n{user_content}\n[/INST]"}
        ]