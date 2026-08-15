import os
import json
import httpx
from typing import Optional, Dict
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import traceback

# Application & Plugin Imports
from app.application.plugin_registry import PluginRegistry
from app.infrastructure.qdrant_service import qdrant_db
from app.domain.models.specification import TaskSpecification
from app.infrastructure.plugins.qwen_local import LocalQwenPlugin
from app.infrastructure.plugins.openrouter import OpenRouterPlugin
from app.infrastructure.plugins.claude_plugin import ClaudePlugin
from app.infrastructure.plugins.openai_plugin import OpenAIPlugin
from app.infrastructure.plugins.gemma_plugin import GemmaPlugin
from app.infrastructure.plugins.deepseek_plugin import DeepSeekPlugin
from app.infrastructure.plugins.llama_plugin import LlamaPlugin
from app.infrastructure.plugins.gpt4_plugin import GPT4Plugin
from app.infrastructure.plugins.grok_plugin import GrokPlugin
from app.infrastructure.plugins.kimi_plugin import KimiPlugin
from app.infrastructure.plugins.mistral_plugin import MistralPlugin
from app.infrastructure.plugins.perplexity_plugin import PerplexityPlugin
from app.infrastructure.plugins.gemini_plugin import GeminiPlugin
from app.infrastructure.plugins.codex_plugin import CodexPlugin
from app.infrastructure.plugins.blackbox_plugin import BlackboxPlugin
from app.infrastructure.plugins.cursor_plugin import CursorPlugin
from app.infrastructure.plugins.copilot_plugin import CopilotPlugin
from app.infrastructure.plugins.microsoft_copilot_plugin import MicrosoftCopilotPlugin

OLLAMA_TIMEOUT = httpx.Timeout(timeout=300.0, connect=15.0)
app = FastAPI(title="PromptOS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

registry = PluginRegistry()
registry.register(CursorPlugin())
registry.register(OpenAIPlugin())
registry.register(ClaudePlugin())
registry.register(GemmaPlugin())
registry.register(DeepSeekPlugin())
registry.register(LlamaPlugin())
registry.register(GPT4Plugin())
registry.register(GrokPlugin())
registry.register(KimiPlugin())
registry.register(MistralPlugin())
registry.register(PerplexityPlugin())
registry.register(GeminiPlugin())
registry.register(CodexPlugin())
registry.register(BlackboxPlugin())
registry.register(CopilotPlugin())
registry.register(MicrosoftCopilotPlugin())

USE_CLOUD_MODELS = os.getenv("USE_CLOUD_MODELS", "false").lower() == "true"
if USE_CLOUD_MODELS:
    registry.register(OpenRouterPlugin())
else:
    registry.register(LocalQwenPlugin())


class CompileRequest(BaseModel):
    user_prompt: str
    target_provider: str = "anthropic"
    skip_clarification: bool = False
    resolved_clarifications: Optional[Dict[str, str]] = None


# --- this helper function to safely clean LLM JSON responses ---
def parse_llm_json(content: str) -> dict:
    """Removes markdown code blocks if the local model wrapped the JSON in them."""
    cleaned = content.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    return json.loads(cleaned.strip())

# --- QWEN PASS 1: The Consultant ---
async def ask_qwen_for_clarifications(user_prompt: str) -> dict:
    system_prompt = (
        "You are a World-Class Expert and professional Consultant and Strategic Planner. You sit down with clients from any industry "
        "to deeply understand their vision, outline a bulletproof plan, and extract the precise details needed to guarantee success. "
        "First, read the client's initial goal and INSTANTLY adopt the absolute best professional persona for their specific request "
        "(e.g., Chief Marketing Officer, Senior Software Architect, Expert Copywriter, Financial Advisor, Master Chef, etc.). "
        "Then, acting exactly as that expert, generate 3 or more highly specific, insightful clarifying questions that extract the missing "
        "requirements needed to write the ultimate AI prompt for this task. "
        "Respond strictly in valid JSON format matching this schema:\n"
        '{"role_assumed": "<Insert the specific role you adopted>", "questions": [{"id": "q1", "question": "..."}]}'
    )

    async with httpx.AsyncClient(timeout=OLLAMA_TIMEOUT) as client:
        response = await client.post(
            "http://host.docker.internal:11434/api/chat",            
            json={
                "model": "qwen2.5:3b",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Client Initial Goal:\n{user_prompt}"}
                ],
                "format": "json",
                "stream": False,
                "keep_alive": "24h",
                "options": {
                    "num_ctx": 4096,
                    "num_predict": 500,  # Questions are short; cap token output for faster responses
                    "temperature": 0.2
                }
            }
        )
        response.raise_for_status()
        raw_content = response.json()["message"]["content"]
        return parse_llm_json(raw_content)
        
 

# --- QWEN PASS 2: The Synthesizer & Organizer ---
async def synthesize_prompt_details(user_prompt: str, answers: dict, rules: list) -> dict:
    answers_str = "\n".join([f"- {k}: {v}" for k, v in answers.items()]) if answers else "None (Direct generation requested)"
    rules_str = "\n".join([f"- {r}" for r in rules]) if rules else "No specific guidelines found."
    
    system_prompt = (
        "You are a World-Class AI Prompt Engineer and Strategic Planner. Take the client's raw idea, the clarifying details "
        "they just provided to your consultant, and any specific formatting guidelines, and organize them into a comprehensive, highly detailed, "
        "and flawlessly structured prompt specification.\n"
        "Your goal is to build a prompt so detailed and well-planned that when the user pastes it into their target AI, they get the best possible result.\n"
        "Output strictly in JSON matching this schema:\n"
        '{\n'
        '  "primary_objective": "A highly detailed, comprehensive expansion of what the target AI needs to do. Write it beautifully.",\n'
        '  "context_data": ["List of background info, personas, target audience, and relevant rules"],\n'
        '  "constraints": ["List of strict formatting, technical boundaries, tone, and operational rules"],\n'
        '  "examples": []\n'
        '}'
    )
    
    user_content = (
        f"Raw Idea: {user_prompt}\n\n"
        f"Client Clarifications:\n{answers_str}\n\n"
        f"Enterprise/Formatting Guidelines to Incorporate:\n{rules_str}"
    )
    
    async with httpx.AsyncClient(timeout=OLLAMA_TIMEOUT) as client:
        response = await client.post(
            "http://host.docker.internal:11434/api/chat",
            json={
                "model": "qwen2.5:3b",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                "format": "json",
                "stream": False,
                "keep_alive": "24h",
                "options": {
                    "num_ctx": 4096,
                    "num_predict": 1500,  # Caps max generation length to prevent hangs
                    "temperature": 0.2
                }
            }
        )
        response.raise_for_status()
        raw_content = response.json()["message"]["content"]
        return parse_llm_json(raw_content)

# ---  this helper function ---
def sanitize_rich_spec(raw: dict) -> dict:
    """Ensures Qwen's JSON output strictly matches TaskSpecification data types."""
    # 1. Ensure primary_objective is a clean string
    obj = raw.get("primary_objective", "")
    if isinstance(obj, dict):
        obj = json.dumps(obj)
    elif not isinstance(obj, str):
        obj = str(obj)

    # 2. Ensure context_data is a list of strings (flatten dicts if Qwen nested them)
    raw_ctx = raw.get("context_data", [])
    clean_ctx = []
    if isinstance(raw_ctx, list):
        for item in raw_ctx:
            if isinstance(item, str):
                clean_ctx.append(item)
            elif isinstance(item, dict):
                clean_ctx.append(", ".join([f"{k}: {v}" for k, v in item.items()]))
            else:
                clean_ctx.append(str(item))
    elif isinstance(raw_ctx, str):
        clean_ctx.append(raw_ctx)

    # 3. Ensure constraints is a list of strings
    raw_const = raw.get("constraints", [])
    clean_const = []
    if isinstance(raw_const, list):
        for item in raw_const:
            if isinstance(item, str):
                clean_const.append(item)
            elif isinstance(item, dict):
                clean_const.append(", ".join([f"{k}: {v}" for k, v in item.items()]))
            else:
                clean_const.append(str(item))
    elif isinstance(raw_const, str):
        clean_const.append(raw_const)

    # 4. Ensure examples is a list of dicts
    raw_ex = raw.get("examples", [])
    clean_ex = []
    if isinstance(raw_ex, list):
        for item in raw_ex:
            if isinstance(item, dict):
                clean_ex.append(item)
            elif isinstance(item, str):
                clean_ex.append({"input": item, "output": ""})

    return {
        "primary_objective": obj,
        "context_data": clean_ctx,
        "constraints": clean_const,
        "examples": clean_ex
    }


@app.post("/api/v1/compile")
async def compile_prompt_endpoint(request: CompileRequest):
    print(f"Incoming request: provider={request.target_provider}, skip_clarification={request.skip_clarification}")
    
    if not request.skip_clarification and not request.resolved_clarifications:
        try:
            clarification_data = await ask_qwen_for_clarifications(request.user_prompt)
            return {
                "requires_clarification": True,
                "intent": clarification_data
            }
        except Exception as e:
            print(f"Local Qwen consultation error (bypassing to compile): {e}")

    relevant_rules = qdrant_db.search_guidelines(request.user_prompt)
    answers = request.resolved_clarifications or {}
    
    try:
        print("Synthesizing final requirements with Qwen...")
        rich_spec = await synthesize_prompt_details(request.user_prompt, answers, relevant_rules)
        
        # Clean and normalize Qwen's output so Pydantic never fails
        clean_spec_data = sanitize_rich_spec(rich_spec)
        
        spec = TaskSpecification(
            category="general", 
            primary_objective=clean_spec_data["primary_objective"],
            context_data=clean_spec_data["context_data"] + relevant_rules, 
            constraints=clean_spec_data["constraints"], 
            examples=clean_spec_data["examples"]     
        )
    except Exception as e:
        
        print(f"Synthesis failed, using raw fallback. Error type: {type(e).__name__}, Details: {e}")
        traceback.print_exc()  # Prints the full stack trace in Docker logs
        answers_text = "\n".join([f"- {q}: {a}" for q, a in answers.items()])
        spec = TaskSpecification(
            category="general",
            primary_objective=f"{request.user_prompt}\n\nDetails:\n{answers_text}",
            context_data=relevant_rules,
            constraints=[],
            examples=[]
        )
    
    try:
        active_plugin = registry.get(request.target_provider)
        chatml_messages = active_plugin.compile_prompt(spec, model_id="default")
        
        formatted_prompt = ""
        for msg in chatml_messages:
            role = msg["role"].upper()
            content = msg["content"]
            formatted_prompt += f"[{role}]\n{content}\n\n"
            
        return {
            "requires_clarification": False,
            "compiled_prompt": request.user_prompt + '\n' + formatted_prompt.strip()
        }
    except Exception as e:
        print(f"AI Execution Error: {str(e)}")
        return {"error": str(e)}
    
