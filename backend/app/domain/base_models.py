from pydantic import BaseModel, Field
from typing import List

class CapabilityProfile(BaseModel):
    capabilities: List[str] = Field(description="e.g., 'vision', 'mcp_support', 'json_mode', 'deep_reasoning'")
    context_window_tokens: int
    pricing_input_1m: float
    pricing_output_1m: float
    latency_tier: str = Field(description="'ultra-low', 'low', 'medium', 'high'")
    reliability_score: float = Field(default=0.99)
    strengths: List[str]
    weaknesses: List[str]
    recommended_tasks: List[str]
    avoid_for: List[str]

class ModelDefinition(BaseModel):
    id: str
    name: str
    provider: str
    profile: CapabilityProfile