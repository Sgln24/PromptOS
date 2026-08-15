import asyncio
import time
from litellm import acompletion, cost_calculator
from typing import List
from app.domain.benchmarking.base_models import BenchmarkReport, ModelExecutionMetrics
from app.domain.models.specification import TaskSpecification
from app.application.plugin_registry import PluginRegistry
import os


class BenchmarkEngine:
    def __init__(self, registry: PluginRegistry):
        self.registry = registry

    async def _execute_single_model(self, spec: TaskSpecification, model_id: str, provider_name: str):
        # 1. Compile the prompt
        plugin = self.registry.get_plugin(provider_name)
        compiled_prompt = plugin.compile_prompt(spec, model_id)
        messages = compiled_prompt if isinstance(compiled_prompt, list) else [{"role": "user", "content": compiled_prompt}]

        # 2. Setup OpenRouter Headers
        # LiteLLM accepts custom headers via the 'extra_headers' dict
        custom_headers = {}
        if provider_name == "openrouter":
            custom_headers = {
                "HTTP-Referer": os.getenv("PROMPTOS_SITE_URL", "http://localhost:3001"),
                "X-Title": os.getenv("PROMPTOS_APP_NAME", "PromptOS")
            }

        # 3. Execute with LiteLLM
        response = await acompletion(
            model=model_id, # e.g., "openrouter/anthropic/claude-3.5-sonnet" or "ollama/qwen"
            messages=messages,
            extra_headers=custom_headers
        )
    
       # ... metrics and cost calculation ...
        
        end_time = time.perf_counter()
        
        # 3. Calculate Metrics
        latency = (end_time - start_time) * 1000
        usage = response.usage
        
        # LiteLLM cost calculation helper
        cost = cost_calculator.completion_cost(completion_response=response) or 0.0

        return ModelExecutionMetrics(
            model_id=model_id,
            provider=provider_name,
            latency_ms=latency,
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
            total_cost_usd=cost,
            raw_response=response.choices[0].message.content
        )

    async def run_benchmark(self, spec: TaskSpecification, targets: List[dict]) -> BenchmarkReport:
        """Runs the compiled prompt against multiple models concurrently."""
        
        tasks = [
            self._execute_single_model(spec, t["model_id"], t["provider"])
            for t in targets
        ]
        
        # Execute in parallel
        results = await asyncio.gather(*tasks, return_exceptions=False)
        
        # Simple heuristic: winner is the cheapest model that didn't fail
        # In a real system, we'd use LLM-as-a-Judge for response quality.
        winner = min(results, key=lambda x: x.total_cost_usd * (x.latency_ms / 1000))

        return BenchmarkReport(
            task_id=spec.primary_objective[:20], # mock ID
            winner_model_id=winner.model_id,
            results=list(results),
            recommendation_reason=f"{winner.model_id} selected for optimal cost-to-latency ratio."
        )