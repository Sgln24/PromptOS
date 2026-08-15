from app.domain.interfaces import ProviderPlugin
from app.domain.base_models import ModelDefinition, CapabilityProfile
from app.domain.models.specification import TaskSpecification
from typing import List, Dict

class CopilotPlugin(ProviderPlugin):
    @property
    def provider_name(self) -> str:
        return "github_copilot"

    def get_supported_models(self) -> List[ModelDefinition]:
        return [
            ModelDefinition(
                id="github-copilot-chat",
                name="GitHub Copilot Chat",
                provider="github_copilot",
                profile=CapabilityProfile(
                    capabilities=["inline_completion", "chat_assistance", "code_explanation", "test_scaffolding"],
                    context_window_tokens=64000,
                    pricing_input_1m=0.0,  # Included in Copilot subscription tiers
                    pricing_output_1m=0.0,
                    latency_tier="fast",
                    strengths=["Seamless IDE context integration", "Exceptional boilerplate generation", "Rapid unit test scaffolding"],
                    weaknesses=["Performance relies heavily on explicit context and incremental task breakdown"],
                    recommended_tasks=["Routine code generation", "Unit test creation", "Code explanation and debugging"],
                    avoid_for=[]
                )
            )
        ]

    def compile_prompt(self, spec: TaskSpecification, model_id: str) -> List[Dict[str, str]]:
        """
        Formats prompts adhering to GitHub Copilot prompt engineering best practices:
        - Clearly state intent and behavior upfront.
        - Anchor contextual rules, files, and enterprise RAG standards.
        - Break complex tasks into incremental, reviewable instructions.
        """
        system_content = (
            f"You are operating on GitHub Copilot model '{model_id}'. "
            "Act as an expert pair programmer. Follow Copilot best practices: state intent clearly, "
            "respect project structure, provide incremental implementation steps, and adhere strictly to enterprise rules."
        )

        user_parts = []

        # 1. Context & Guidelines (Deliberate context anchoring)
        if spec.context_data:
            rules_text = "\n".join([f"- {rule}" for rule in spec.context_data])
            user_parts.append(f"### Context & Guidelines\n{rules_text}")

        # 2. Constraints & Technical Boundaries
        if spec.constraints:
            constraints_text = "\n".join([f"- {c}" for c in spec.constraints])
            user_parts.append(f"### Constraints\n{constraints_text}")

        # 3. Examples
        if spec.examples:
            examples_text = ""
            for ex in spec.examples:
                examples_text += f"Input: {ex.get('input')}\nOutput: {ex.get('output')}\n\n"
            user_parts.append(f"### Examples\n{examples_text}")

        # 4. Task Objective / Intent
        user_parts.append(f"### Task Objective & Implementation Intent\n{spec.primary_objective}")

        user_content = "\n\n".join(user_parts)

        return [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content}
        ]