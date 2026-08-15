from app.domain.interfaces import ProviderPlugin
from app.domain.base_models import ModelDefinition, CapabilityProfile
from app.domain.models.specification import TaskSpecification
from typing import List, Dict

class CodexPlugin(ProviderPlugin):
    @property
    def provider_name(self) -> str:
        return "openai_codex"

    def get_supported_models(self) -> List[ModelDefinition]:
        return [
            ModelDefinition(
                id="codex-max",
                name="OpenAI Codex Max",
                provider="openai_codex",
                profile=CapabilityProfile(
                    capabilities=["code_generation", "agentic_autonomy", "multi_file_refactoring", "test_verification"],
                    context_window_tokens=200000,
                    pricing_input_1m=1.50,
                    pricing_output_1m=6.00,
                    latency_tier="slow",
                    strengths=["Autonomous multi-hour reasoning", "Rigorous adherence to architectural constraints", "Precise test-driven development"],
                    weaknesses=["Requires explicitly defined completion criteria to prevent premature stopping"],
                    recommended_tasks=["Full feature implementation", "Complex multi-file refactoring", "Automated code generation"],
                    avoid_for=[]
                )
            )
        ]

    def compile_prompt(self, spec: TaskSpecification, model_id: str) -> List[Dict[str, str]]:
        """
        Formats prompts adhering to OpenAI Codex prompt engineering best practices:
        - Front-loads instructions and uses distinct triple-quote delimiters.
        - Structures the prompt into Goal, Context, Constraints, and Completion Criteria.
        """
        system_content = (
            f"You are operating on OpenAI Codex model '{model_id}'. "
            "Act as an expert autonomous software engineer. Follow the 4-element prompt structure strictly: Goal, Context, Constraints, and Done When."
        )

        user_parts = []

        # 1. Context (Enterprise Guidelines & References)
        if spec.context_data:
            rules_text = "\n".join([f"- {rule}" for rule in spec.context_data])
            user_parts.append(f"### Context\n\"\"\"\n{rules_text}\n\"\"\"")

        # 2. Constraints (Architectural rules & limits)
        if spec.constraints:
            constraints_text = "\n".join([f"- {c}" for c in spec.constraints])
            user_parts.append(f"### Constraints\n{constraints_text}")

        # 3. Examples
        if spec.examples:
            examples_text = ""
            for ex in spec.examples:
                examples_text += f"Input: {ex.get('input')}\nOutput: {ex.get('output')}\n\n"
            user_parts.append(f"### Examples\n{examples_text}")

        # 4. Goal & Completion Criteria ("Done When")
        goal_block = (
            f"### Goal\n{spec.primary_objective}\n\n"
            "### Done When\n"
            "- All operational guidelines and enterprise constraints are fully met.\n"
            "- The task execution is verified, complete, and produces no syntax or logical errors."
        )
        user_parts.append(goal_block)

        final_user_message = "\n\n".join(user_parts)

        return [
            {"role": "system", "content": system_content},
            {"role": "user", "content": final_user_message}
        ]