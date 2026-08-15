from app.domain.interfaces import ProviderPlugin
from app.domain.base_models import ModelDefinition, CapabilityProfile
from app.domain.models.specification import TaskSpecification
from typing import List, Dict

class GeminiPlugin(ProviderPlugin):
    @property
    def provider_name(self) -> str:
        return "google_gemini"

    def get_supported_models(self) -> List[ModelDefinition]:
        return [
            ModelDefinition(
                id="gemini-2.5-pro",
                name="Gemini 2.5 Pro",
                provider="google_gemini",
                profile=CapabilityProfile(
                    capabilities=["multimodal", "ultra_long_context", "deep_reasoning", "structured_outputs"],
                    context_window_tokens=2000000,
                    pricing_input_1m=1.25,
                    pricing_output_1m=5.00,
                    latency_tier="balanced",
                    strengths=["2M+ token context window", "Exceptional long-context recall", "Native multimodal synthesis"],
                    weaknesses=[],
                    recommended_tasks=["Massive document analysis", "Codebase ingestion", "Complex enterprise RAG"],
                    avoid_for=[]
                )
            ),
            ModelDefinition(
                id="gemini-2.5-flash",
                name="Gemini 2.5 Flash",
                provider="google_gemini",
                profile=CapabilityProfile(
                    capabilities=["speed", "multimodal", "high_volume", "cost_efficient"],
                    context_window_tokens=1000000,
                    pricing_input_1m=0.075,
                    pricing_output_1m=0.30,
                    latency_tier="fast",
                    strengths=["Blazing fast inference", "High performance-to-cost ratio", "Massive context support"],
                    weaknesses=["Lower reasoning depth on complex frontier logic compared to Pro"],
                    recommended_tasks=["Real-time data extraction", "High-throughput classification", "Fast multimodal tasks"],
                    avoid_for=[]
                )
            )
        ]

    def compile_prompt(self, spec: TaskSpecification, model_id: str) -> List[Dict[str, str]]:
        """
        Formats prompts adhering to Google's official Gemini and Vertex AI prompting guide:
        - Place behavioral constraints and role definitions in the System Instruction.
        - Use clear XML-style tags for consistent layout.
        - For RAG/long-context structures, place data context first and anchor the query at the end.
        """
        system_content = (
            f"You are operating on Google Gemini model '{model_id}'. "
            "Be precise, direct, and efficient. Follow all operational constraints and enterprise guidelines strictly."
        )

        user_parts = []

        # 1. Enterprise Context / RAG Guidelines (Placed first for optimal long-context anchoring)
        if spec.context_data:
            rules_xml = "\n".join([f"  <rule>{rule}</rule>" for rule in spec.context_data])
            user_parts.append(f"<enterprise_context>\n{rules_xml}\n</enterprise_context>")

        # 2. Constraints & Parameters
        if spec.constraints:
            constraints_xml = "\n".join([f"  <constraint>{c}</constraint>" for c in spec.constraints])
            user_parts.append(f"<constraints>\n{constraints_xml}\n</constraints>")

        # 3. Few-Shot Examples
        if spec.examples:
            examples_xml = ""
            for ex in spec.examples:
                examples_xml += f"  <example>\n    <input>{ex.get('input')}</input>\n    <output>{ex.get('output')}</output>\n  </example>\n"
            user_parts.append(f"<examples>\n{examples_xml}</examples>")

        # 4. Context Anchoring & Core Objective (Placed at the end per Gemini long-context best practices)
        objective_block = (
            "Based on the enterprise context and parameters provided above, complete the following task:\n\n"
            f"<objective>\n{spec.primary_objective}\n</objective>"
        )
        user_parts.append(objective_block)

        final_user_message = "\n\n".join(user_parts)

        return [
            {"role": "system", "content": system_content},
            {"role": "user", "content": final_user_message}
        ]