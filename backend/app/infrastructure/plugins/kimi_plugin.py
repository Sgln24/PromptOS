from app.domain.interfaces import ProviderPlugin
from app.domain.base_models import ModelDefinition, CapabilityProfile
from app.domain.models.specification import TaskSpecification
from typing import List, Dict

class KimiPlugin(ProviderPlugin):
    @property
    def provider_name(self) -> str:
        return "moonshot"

    def get_supported_models(self) -> List[ModelDefinition]:
        return [
            ModelDefinition(
                id="moonshotai/kimi-k2.5",
                name="Kimi K2.5",
                provider="moonshot",
                profile=CapabilityProfile(
                    capabilities=["multimodal", "agentic_orchestration", "parallel_tasks", "long_context", "vision_text_co_optimization"],
                    context_window_tokens=262000,
                    pricing_input_1m=0.375,
                    pricing_output_1m=2.025,
                    latency_tier="balanced",
                    strengths=["Native text-vision co-optimization", "Agent Swarm parallel task execution", "Strong instruction following"],
                    weaknesses=["Complex agent workflows require clear step-by-step task decomposition"],
                    recommended_tasks=["Multimodal data extraction", "Parallel agentic workflows", "Complex document summarization"],
                    avoid_for=[]
                )
            )
        ]

    def compile_prompt(self, spec: TaskSpecification, model_id: str) -> List[Dict[str, str]]:
        """
        Formats prompts adhering to Moonshot AI Kimi K2.5 guidelines:
        - Clarify role and context explicitly.
        - Describe tasks specifically with explicit output formats.
        - Break down complex multi-step objectives systematically for agentic execution.
        """
        system_content = (
            f"You are operating on Moonshot AI model '{model_id}' with native multimodal and agentic orchestration capabilities. "
            "Execute the task with rigorous clarity, structural precision, and step-by-step task breakdown."
        )

        user_parts = []

        # 1. Enterprise RAG Guidelines / Context
        if spec.context_data:
            rules_text = "\n".join([f"- {rule}" for rule in spec.context_data])
            user_parts.append(f"### Context & Guidelines\n{rules_text}")

        # 2. Constraints
        if spec.constraints:
            constraints_text = "\n".join([f"- {c}" for c in spec.constraints])
            user_parts.append(f"### Constraints & Requirements\n{constraints_text}")

        # 3. Examples
        if spec.examples:
            examples_text = ""
            for ex in spec.examples:
                examples_text += f"Input: {ex.get('input')}\nOutput: {ex.get('output')}\n\n"
            user_parts.append(f"### Examples\n{examples_text}")

        # 4. Core Objective / Task Description
        user_parts.append(f"### Task Objective\n{spec.primary_objective}")

        user_content = "\n\n".join(user_parts)

        return [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content}
        ]