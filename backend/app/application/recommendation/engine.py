from typing import List
from app.application.plugin_registry import PluginRegistry
from app.application.intent.analyzer import ExtractedIntent
from app.domain.recommendation.base_models import RecommendationResult, ModelScore

class ModelRecommendationEngine:
    """
    Ranks models based on Capability Profile coverage, Context Window capacity,
    Pricing, and Reliability—never based on provider popularity.
    """

    def __init__(self, registry: PluginRegistry):
        self.registry = registry

    def recommend(self, intent: ExtractedIntent) -> RecommendationResult:
        all_models = self.registry.get_all_capabilities()
        scored_models = []
        required_caps = set(intent.required_capabilities)

        for m in all_models:
            profile = m.profile
            model_caps = set(profile.capabilities)
            reasons = []

            # 1. Capability Match Score
            if required_caps:
                matched = required_caps.intersection(model_caps)
                cap_ratio = len(matched) / len(required_caps)
                missing = required_caps - model_caps
                if matched:
                    reasons.append(f"Supports required capabilities: {', '.join(matched)}.")
                if missing:
                    reasons.append(f"Lacks required capabilities: {', '.join(missing)}.")
            else:
                cap_ratio = 1.0
                reasons.append("Meets default capability requirements.")

            # 2. Context Window Fit
            context_fit = profile.context_window_tokens >= intent.estimated_context_tokens
            if not context_fit:
                reasons.append(f"Context window ({profile.context_window_tokens} tokens) is smaller than estimated needed context ({intent.estimated_context_tokens} tokens).")

            # 3. Latency & Price Weights
            pricing_score = max(0.1, 1.0 - (profile.pricing_input_1m / 20.0))
            
            # Weighted overall score
            total_score = (cap_ratio * 0.50) + (1.0 if context_fit else 0.0) * 0.30 + (pricing_score * 0.20)

            scored_models.append(ModelScore(
                model=m,
                total_score=round(total_score, 3),
                capability_match_ratio=cap_ratio,
                context_fit=context_fit,
                pricing_score=pricing_score,
                reasoning=reasons
            ))

        # --- SAFETY GUARD ADDED HERE ---
        if not scored_models:
            raise ValueError(f"No models available for execution mode. Check your registered plugins.")

        # Sort descending by total score
        scored_models.sort(key=lambda x: x.total_score, reverse=True)

        primary = scored_models[0]
        alternatives = scored_models[1:3]

        justification = (
            f"Recommended '{primary.model.name}' ({primary.model.provider}) with a score of {primary.total_score}. "
            f"Reason: {primary.reasoning[0]}"
        )

        return RecommendationResult(
            primary_recommendation=primary,
            alternatives=alternatives,
            summary_justification=justification
        )