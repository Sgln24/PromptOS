from app.domain.interfaces import ProviderPlugin
from app.domain.base_models import ModelDefinition, CapabilityProfile
from app.domain.models.specification import TaskSpecification
from typing import List, Dict

class DeepSeekPlugin(ProviderPlugin):
    @property
    def provider_name(self) -> str:
        return "deepseek"

    def get_supported_models(self) -> List[ModelDefinition]:
        return [
            ModelDefinition(
                id="deepseek-reasoner",
                name="DeepSeek R1 (Reasoner)",
                provider="deepseek",
                profile=CapabilityProfile(
                    capabilities=["chain_of_thought", "advanced_reasoning", "math", "coding"],
                    context_window_tokens=64000,
                    pricing_input_1m=0.55,
                    pricing_output_1m=2.19,
                    latency_tier="slow",
                    strengths=["Native chain-of-thought reasoning", "Exceptional cost-to-performance ratio for logic"],
                    weaknesses=["Avoid manual step-by-step CoT hand-holding"],
                    recommended_tasks=["Complex mathematical problem solving", "Deep architectural reasoning", "Logic tasks"],
                    avoid_for=[]
                )
            ),
            ModelDefinition(
                id="deepseek-chat",
                name="DeepSeek V3 (Chat)",
                provider="deepseek",
                profile=CapabilityProfile(
                    capabilities=["general_chat", "coding", "multilingual", "fast_response"],
                    context_window_tokens=64000,
                    pricing_input_1m=0.14,
                    pricing_output_1m=0.28,
                    latency_tier="fast",
                    strengths=["Blazing fast response times", "Extremely cost-effective general intelligence"],
                    weaknesses=[],
                    recommended_tasks=["General text generation", "Fast coding assistance", "Conversational flows"],
                    avoid_for=[]
                )
            )
        ]

    def compile_prompt(self, spec: TaskSpecification, model_id: str) -> List[Dict[str, str]]:
        """
        Formats prompts adhering to DeepSeek's official reasoning guidelines:
        - Keeps system prompts concise (durable behavior and role definition).
        - Uses clean markdown sections for RAG context and constraints so reasoning models (like R1) can parse them cleanly.
        """
        system_content = (
            f"You are operating on DeepSeek model '{model_id}'. "
            "Think deeply and logically through the problem internally before providing your final output."
        )

        user_parts = []

        # 1. Enterprise RAG Context / Guidelines
        if spec.context_data:
            rules_text = "\n".join([f"- {rule}" for rule in spec.context_data])
            user_parts.append(f"### Context & Guidelines\n{rules_text}")

        # 2. Constraints
        if spec.constraints:
            constraints_text = "\n".join([f"- {c}" for c in spec.constraints])
            user_parts.append(f"### Constraints\n{constraints_text}")

        # 3. Examples
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