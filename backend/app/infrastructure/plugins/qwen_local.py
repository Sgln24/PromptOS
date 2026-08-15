from app.domain.interfaces import ProviderPlugin
from app.domain.base_models import ModelDefinition, CapabilityProfile
from app.domain.models.specification import TaskSpecification
from typing import List, Dict

class LocalQwenPlugin(ProviderPlugin):
    @property
    def provider_name(self) -> str:
        return "qwen_local"

    def get_supported_models(self) -> List[ModelDefinition]:
        return [
            ModelDefinition(
                # The 'ollama/' prefix tells LiteLLM how to route the request
                id="ollama/qwen", 
                name="Qwen Local",
                provider="qwen_local",
                profile=CapabilityProfile(
                    capabilities=[
                        "coding", 
                        "multilingual", 
                        "chinese_language", 
                        "spanish_language", 
                        "local_privacy"
                    ],
                    context_window_tokens=32000,
                    pricing_input_1m=0.0,  # 100% Free
                    pricing_output_1m=0.0, # 100% Free
                    latency_tier="low",
                    strengths=[
                        "Zero data egress (highly private)", 
                        "Excellent multilingual reasoning", 
                        "Strong Python/FastAPI code generation"
                    ],
                    weaknesses=["Hardware dependent for inference speed"],
                    recommended_tasks=["Programming", "Translation", "Local Data Processing"],
                    avoid_for=["Tasks requiring live internet access"]
                )
            )
        ]

    def compile_prompt(self, spec: TaskSpecification, model_id: str) -> List[Dict[str, str]]:
        """
        Qwen responds very well to the standard ChatML format, 
        which maps cleanly to OpenAI-style message arrays.
        """
        messages = []
        
        # Build System Prompt
        system_content = "You are a highly capable AI assistant."
        if spec.role_persona:
            system_content = f"Role: {spec.role_persona}\n"
            
        if spec.constraints:
            system_content += "\nStrict Constraints:\n" + "\n".join([f"- {c}" for c in spec.constraints])
            
        messages.append({"role": "system", "content": system_content.strip()})
        
        # Inject Examples
        for ex in spec.examples:
            messages.append({"role": "user", "content": ex['input']})
            messages.append({"role": "assistant", "content": ex['output']})
            
        # Build Final User Message
        user_content = f"Task:\n{spec.primary_objective}\n"
        if spec.context_data:
            user_content += "\nContext:\n" + "\n---\n".join(spec.context_data)
            
        messages.append({"role": "user", "content": user_content.strip()})
        
        return messages