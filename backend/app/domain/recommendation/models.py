from pydantic import BaseModel, Field
from typing import List, Dict
from app.domain.base_models import ModelDefinition

class ModelScore(BaseModel):
    model: ModelDefinition
    total_score: float = Field(description="Normalized score between 0.0 and 1.0")
    capability_match_ratio: float
    context_fit: bool
    pricing_score: float
    reasoning: List[str] = Field(description="Explicit justifications for why this model fits or fails")

class RecommendationResult(BaseModel):
    primary_recommendation: ModelScore
    alternatives: List[ModelScore]
    summary_justification: str