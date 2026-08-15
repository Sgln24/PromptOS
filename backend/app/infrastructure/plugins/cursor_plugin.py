from app.domain.interfaces import ProviderPlugin
from app.domain.base_models import ModelDefinition, CapabilityProfile
from app.domain.models.specification import TaskSpecification
from typing import List, Dict

class CursorPlugin(ProviderPlugin):
    @property
    def provider_name(self) -> str:
        return "cursor"

    def get_supported_models(self) -> List[ModelDefinition]:
        return [
            ModelDefinition(
                id="cursor-agent",
                name="Cursor AI Agent (Composer)",
                provider="cursor",
                profile=CapabilityProfile(
                    capabilities=["codebase_indexing", "multi_file_editing", "terminal_execution", "plan_mode"],
                    context_window_tokens=200000,
                    pricing_input_1m=0.0,  # IDE-native routing layer
                    pricing_output_1m=0.0,
                    latency_tier="fast",
                    strengths=["Deep codebase awareness via vector search", "Autonomous multi-file refactoring", "Plan-first execution"],
                    weaknesses=["Requires explicit non-goals to prevent unwanted scope expansion"],
                    recommended_tasks=["Full stack feature implementation", "Test-driven development", "Codebase migrations"],
                    avoid_for=[]
                )
            )
        ]

    def compile_prompt(self, spec: TaskSpecification, model_id: str) -> List[Dict[str, str]]:
        """
        Formats prompts adhering to Cursor's AI coding best practices:
        - Start with a tight, specific goal.
        - Anchor context to reliable enterprise guidelines and file rules.
        - Explicitly declare constraints and non-goals.
        - Structure output for plan-first or direct execution.
        """
        system_content = (
            f"You are operating within Cursor IDE on model '{model_id}'. "
            "Act as an expert software engineer. Follow Cursor best practices: adhere strictly to the codebase patterns, "
            "respect non-goals, and propose a concise implementation plan before modifying multiple files if the task is non-trivial."
        )

        user_parts = []

        # 1. Codebase Context & Enterprise RAG Guidelines
        if spec.context_data:
            rules_text = "\n".join([f"- {rule}" for rule in spec.context_data])
            user_parts.append(f"### Codebase Context & Guidelines\n{rules_text}")

        # 2. Constraints & Non-Goals
        if spec.constraints:
            constraints_text = "\n".join([f"- {c}" for c in spec.constraints])
            user_parts.append(f"### Constraints & Non-Goals\n{constraints_text}\n- Non-Goal: Do not alter code outside the requested scope or refactor unrelated files.")

        # 3. Examples
        if spec.examples:
            examples_text = ""
            for ex in spec.examples:
                examples_text += f"Input: {ex.get('input')}\nOutput: {ex.get('output')}\n\n"
            user_parts.append(f"### Reference Examples\n{examples_text}")

        # 4. Tight Goal / Objective
        user_parts.append(f"### Goal\n{spec.primary_objective}")

        user_content = "\n\n".join(user_parts)

        return [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content}
        ]