from app.domain.interfaces import ProviderPlugin
from app.domain.base_models import ModelDefinition, CapabilityProfile
from app.domain.models.specification import TaskSpecification
from typing import List, Dict

class BlackboxPlugin(ProviderPlugin):
    @property
    def provider_name(self) -> str:
        return "blackbox"

    def get_supported_models(self) -> List[ModelDefinition]:
        return [
            ModelDefinition(
                id="blackbox-code-agent",
                name="BLACKBOX AI Coder & Agent",
                provider="blackbox",
                profile=CapabilityProfile(
                    capabilities=["code_generation", "intent_parsing", "debugging", "git_context"],
                    context_window_tokens=128000,
                    pricing_input_1m=0.50,
                    pricing_output_1m=1.50,
                    latency_tier="fast",
                    strengths=["Instant context integration from files/git", "Precise intent parsing (generate, debug, refactor)", "Developer-first code completion"],
                    weaknesses=["Optimized primarily for coding and technical workflows rather than general creative writing"],
                    recommended_tasks=["Code generation", "Bug debugging", "Git-aware code analysis"],
                    avoid_for=[]
                )
            )
        ]

    def compile_prompt(self, spec: TaskSpecification, model_id: str) -> List[Dict[str, str]]:
        """
        Formats prompts adhering to BLACKBOX AI coding and agent best practices:
        - Front-loads rich context (code structure, rules, guidelines).
        - Explicitly frames intent (generate, debug, refactor, explain).
        - Structures rules and constraints cleanly for development workflows.
        """
        system_content = (
            f"You are operating on BLACKBOX AI model '{model_id}'. "
            "Act as an expert developer assistant. Parse intent accurately (generate, debug, refactor, or explain) "
            "and leverage the provided rich context and constraints for clean, high-performance code."
        )

        user_parts = []

        # 1. Rich Context & Guidelines (RAG/Code context)
        if spec.context_data:
            rules_text = "\n".join([f"- {rule}" for rule in spec.context_data])
            user_parts.append(f"### Code Context & Guidelines\n{rules_text}")

        # 2. Constraints & Code Standards
        if spec.constraints:
            constraints_text = "\n".join([f"- {c}" for c in spec.constraints])
            user_parts.append(f"### Coding Constraints\n{constraints_text}")

        # 3. Examples
        if spec.examples:
            examples_text = ""
            for ex in spec.examples:
                examples_text += f"Input: {ex.get('input')}\nOutput: {ex.get('output')}\n\n"
            user_parts.append(f"### Reference Examples\n{examples_text}")

        # 4. Core Objective / Task Intent
        user_parts.append(f"### Task Objective\n{spec.primary_objective}")

        user_content = "\n\n".join(user_parts)

        return [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content}
        ]