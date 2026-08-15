from app.domain.interfaces import ProviderPlugin
from app.domain.base_models import ModelDefinition, CapabilityProfile
from app.domain.models.specification import TaskSpecification
from typing import List, Dict

class PerplexityPlugin(ProviderPlugin):
    @property
    def provider_name(self) -> str:
        return "perplexity"

    def get_supported_models(self) -> List[ModelDefinition]:
        return [
            ModelDefinition(
                id="sonar-pro",
                name="Sonar Pro (Search & Synthesis)",
                provider="perplexity",
                profile=CapabilityProfile(
                    capabilities=["live_web_search", "synthesis", "deep_research", "citation_tracking"],
                    context_window_tokens=127000,
                    pricing_input_1m=3.0,
                    pricing_output_1m=15.0,
                    latency_tier="fast",
                    strengths=["Real-time web search integration", "Precise source grounding and citation", "Comprehensive multi-source synthesis"],
                    weaknesses=["Relies on retrieval quality for dynamic facts"],
                    recommended_tasks=["Up-to-date market research", "Technological watch", "Live data grounding"],
                    avoid_for=[]
                )
            ),
            ModelDefinition(
                id="sonar-reasoning-pro",
                name="Sonar Reasoning Pro",
                provider="perplexity",
                profile=CapabilityProfile(
                    capabilities=["live_web_search", "deep_reasoning", "chain_of_thought", "citation_tracking"],
                    context_window_tokens=127000,
                    pricing_input_1m=2.0,
                    pricing_output_1m=8.0,
                    latency_tier="slow",
                    strengths=["Combined live search and advanced chain-of-thought", "Rigorous step-by-step logic"],
                    weaknesses=["Higher latency due to reasoning and search loops"],
                    recommended_tasks=["Complex analytical queries requiring live data", "Fact-checked technical research"],
                    avoid_for=[]
                )
            )
        ]

    def compile_prompt(self, spec: TaskSpecification, model_id: str) -> List[Dict[str, str]]:
        """
        Formats prompts adhering to Perplexity's Sonar API & Prompt Guide best practices:
        - Provide clear context and disambiguation to improve retrieval accuracy.
        - Structure enterprise RAG rules and constraints using clean markdown sections.
        """
        system_content = (
            f"You are operating on Perplexity model '{model_id}' with live web search and synthesis capabilities. "
            "Synthesize precise answers with clear context, rigorous adherence to guidelines, and grounded analysis."
        )

        user_parts = []

        # 1. Enterprise Guidelines / Context (Grounding information)
        if spec.context_data:
            rules_text = "\n".join([f"- {rule}" for rule in spec.context_data])
            user_parts.append(f"### Operational Guidelines & Context\n{rules_text}")

        # 2. Constraints & Rules
        if spec.constraints:
            constraints_text = "\n".join([f"- {c}" for c in spec.constraints])
            user_parts.append(f"### Constraints\n{constraints_text}")

        # 3. Examples
        if spec.examples:
            examples_text = ""
            for ex in spec.examples:
                examples_text += f"Input: {ex.get('input')}\nOutput: {ex.get('output')}\n\n"
            user_parts.append(f"### Examples\n{examples_text}")

        # 4. Core Objective / Query Intent
        user_parts.append(f"### Task Objective\n{spec.primary_objective}")

        user_content = "\n\n".join(user_parts)

        return [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content}
        ]