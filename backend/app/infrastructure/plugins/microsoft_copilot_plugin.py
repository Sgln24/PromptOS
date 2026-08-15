from app.domain.interfaces import ProviderPlugin
from app.domain.base_models import ModelDefinition, CapabilityProfile
from app.domain.models.specification import TaskSpecification
from typing import List, Dict


class MicrosoftCopilotPlugin(ProviderPlugin):
    @property
    def provider_name(self) -> str:
        return "microsoft_copilot"

    def get_supported_models(self) -> List[ModelDefinition]:
        return [
            ModelDefinition(
                id="microsoft-copilot-m365",
                name="Microsoft Copilot (M365)",
                provider="microsoft_copilot",
                profile=CapabilityProfile(
                    capabilities=[
                        "graph_grounding",
                        "document_synthesis",
                        "office_automation",
                        "enterprise_search",
                    ],
                    context_window_tokens=128000,
                    pricing_input_1m=0.0,
                    pricing_output_1m=0.0,
                    latency_tier="balanced",
                    strengths=[
                        "Deep Microsoft Graph integration",
                        "Seamless Office 365 file grounding",
                        "Structured business output generation",
                    ],
                    weaknesses=[
                        "Performs best with strict adherence to the Goal-Context-Source-Expectations layout"
                    ],
                    recommended_tasks=[
                        "Enterprise report generation",
                        "Meeting summarization",
                        "Email drafting and scheduling",
                    ],
                    avoid_for=[],
                ),
            )
        ]

    def compile_prompt(
        self, spec: TaskSpecification, model_id: str
    ) -> List[Dict[str, str]]:
        """
        Formats prompts adhering to Microsoft Copilot's official prompting framework:
        - Goal: Clearly state the intended outcome.
        - Context: Background, situation, or user persona.
        - Source: Identify specific data or reference guidelines.
        - Expectations: Specify formatting, structure, tone, and length.
        """
        system_content = (
            f"You are operating on Microsoft Copilot model '{model_id}' integrated with Microsoft Graph. "
            "Act as a professional enterprise collaborator. Structure your responses precisely following the "
            "Goal, Context, Source, and Expectations framework."
        )

        user_parts = []

        # 1. Source (Enterprise RAG Guidelines / References)
        if spec.context_data:
            rules_text = "\n".join(f"- {rule}" for rule in spec.context_data)
            user_parts.append(f"### Source / Reference Data\n{rules_text}")

        # 2. Context (Background / Situation / Constraints)
        if spec.constraints:
            constraints_text = "\n".join(f"- {c}" for c in spec.constraints)
            user_parts.append(
                f"### Context & Operational Constraints\n{constraints_text}"
            )

        # 3. Examples
        if spec.examples:
            examples_text = ""
            for ex in spec.examples:
                examples_text += (
                    f"Input: {ex.get('input')}\n"
                    f"Output: {ex.get('output')}\n\n"
                )
            user_parts.append(f"### Examples\n{examples_text}")

        # 4. Goal & Expectations (Task objective and output rules)
        goal_block = (
            f"### Goal\n{spec.primary_objective}\n\n"
            "### Expectations\n"
            "- Ensure the response is professional, actionable, and tailored to business productivity workflows.\n"
            "- Adhere strictly to the provided source data and operational constraints."
        )
        user_parts.append(goal_block)

        user_content = "\n\n".join(user_parts)

        return [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content},
        ]