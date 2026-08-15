from pydantic import BaseModel
from typing import Dict, Any, List

class ModelExecutionMetrics(BaseModel):
    model_id: str
    provider: str
    latency_ms: float
    prompt_tokens: int
    completion_tokens: int
    total_cost_usd: float
    raw_response: str
    format_adherence_score: float = 1.0  # 1.0 if adhered to requested schema (e.g., JSON)

class BenchmarkReport(BaseModel):
    task_id: str
    winner_model_id: str
    results: List[ModelExecutionMetrics]
    recommendation_reason: str