from app.domain.interfaces import ProviderPlugin
from app.domain.base_models import ModelDefinition, CapabilityProfile
from app.domain.models.specification import TaskSpecification
from typing import List, Dict

class ClaudePlugin(ProviderPlugin):
    @property
    def provider_name(self) -> str:
        return "anthropic"

    def get_supported_models(self) -> List[ModelDefinition]:
        return [
            ModelDefinition(
                id="claude-sonnet-5",
                name="Claude Sonnet 5",
                provider="anthropic",
                profile=CapabilityProfile(
                    capabilities=["adaptive_thinking", "coding", "literal_precision", "agentic_workflows"],
                    context_window_tokens=1000000,
                    pricing_input_1m=3.0,
                    pricing_output_1m=15.0,
                    latency_tier="balanced",
                    strengths=["Adaptive thinking on by default", "Precise literal adherence", "Exceptional agentic loops"],
                    weaknesses=["Does not accept custom sampling parameters (temperature/top_p)"],
                    recommended_tasks=["Production RAG apps", "Complex multi-step coding", "Exhaustive task execution"],
                    avoid_for=[]
                )
            ),
            ModelDefinition(
                id="claude-opus-5",
                name="Claude Opus 5",
                provider="anthropic",
                profile=CapabilityProfile(
                    capabilities=["coding", "enterprise_reasoning", "complex_agents", "long_horizon"],
                    context_window_tokens=1000000,
                    pricing_input_1m=5.0,
                    pricing_output_1m=25.0,
                    latency_tier="slow",
                    strengths=["Autonomous multi-file refactoring", "Long-horizon agentic tasks", "Self-verification"],
                    weaknesses=[],
                    recommended_tasks=["Enterprise architecture", "End-to-end feature engineering"],
                    avoid_for=[]
                )
            ),
            ModelDefinition(
                id="claude-opus-4-8",
                name="Claude Opus 4.8",
                provider="anthropic",
                profile=CapabilityProfile(
                    capabilities=["literal_precision", "long_context", "complex_reasoning", "adaptive_thinking"],
                    context_window_tokens=1000000,
                    pricing_input_1m=5.0,
                    pricing_output_1m=25.0,
                    latency_tier="slow",
                    strengths=["Literal-minded predictability", "High fidelity tool use", "Adaptive thinking control"],
                    weaknesses=["Will not infer unstated scope extensions"],
                    recommended_tasks=["Compliance-sensitive work", "Precise code refactoring", "Long-context RAG"],
                    avoid_for=[]
                )
            )
        ]

    def compile_prompt(self, spec: TaskSpecification, model_id: str) -> List[Dict[str, str]]:
        """
        Formats prompts incorporating Claude Sonnet 5 and Opus best practices:
        - For Sonnet 5 & Opus 4.8: Enforces explicit literal-minded scope directives.
        - Structures stable enterprise RAG context at the top for cache optimization.
        """
        
        if "sonnet-5" in model_id:
            system_prompt = (
                f"You are operating on model '{model_id}' with adaptive thinking enabled. "
                "Interpret all instructions literally and explicitly; apply instructions comprehensively across the full scope requested without missing items."
            )
        elif "opus-4-8" in model_id:
            system_prompt = (
                f"You are operating on model '{model_id}'. "
                "You take instructions literally; apply instructions comprehensively across the full scope requested."
            )
        else:
            system_prompt = (
                f"You are operating on model '{model_id}'. "
                "Execute the complete task end-to-end with high autonomy."
            )

        user_content_parts = []

        # 1. Stable Enterprise RAG Context (Cache-up layout at the top)
        if spec.context_data:
            rules_xml = "\n".join([f"  <rule>{rule}</rule>" for rule in spec.context_data])
            user_content_parts.append(f"<enterprise_context>\n{rules_xml}\n</enterprise_context>")

        # 2. Constraints
        if spec.constraints:
            constraints_xml = "\n".join([f"  <constraint>{c}</constraint>" for c in spec.constraints])
            user_content_parts.append(f"<constraints>\n{constraints_xml}\n</constraints>")

        # 3. Examples
        if spec.examples:
            examples_xml = ""
            for ex in spec.examples:
                examples_xml += f"  <example>\n    <input>{ex.get('input')}</input>\n    <output>{ex.get('output')}</output>\n  </example>\n"
            user_content_parts.append(f"<examples>\n{examples_xml}</examples>")

        # 4. Core Objective with literal/exhaustive scoping note for literal models
        objective_text = spec.primary_objective
        if "sonnet-5" in model_id or "opus-4-8" in model_id:
            objective_text += "\n\n[Execution Note: Ensure instructions are applied exhaustively across every matching item/section within scope.]"

        user_content_parts.append(f"<objective>\n{objective_text}\n</objective>")

        final_user_message = "\n\n".join(user_content_parts)

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": final_user_message}
        ]