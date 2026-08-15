from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from app.domain.models.specification import TaskCategory

class ExtractedIntent(BaseModel):
    raw_prompt: str
    primary_objective: str
    category: TaskCategory
    required_capabilities: List[str] = Field(
        default_factory=list,
        description="Capabilities required, e.g. ['pdf_understanding', 'json_mode', 'deep_reasoning']"
    )
    estimated_context_tokens: int = 4000
    extracted_constraints: List[str] = Field(default_factory=list)
    confidence_score: float = Field(ge=0.0, le=1.0)
    missing_fields: List[str] = Field(default_factory=list)
    detected_ambiguities: List[str] = Field(default_factory=list)

class IntentAnalyzer:
    """
    Parses unstructured user requests into structured Intent and required Capabilities.
    Uses rule-based heuristics and AST parsing for offline speed, with LLM fallbacks.
    """
    
    CAPABILITY_KEYWORD_MAP = {
        "pdf": "pdf_understanding",
        "document": "pdf_understanding",
        "json": "json_mode",
        "schema": "structured_output",
        "code": "coding",
        "python": "coding",
        "refactor": "coding",
        "image": "vision",
        "photo": "vision",
        "diagram": "vision",
        "mcp": "mcp_support",
        "tool": "tool_calling",
        "function": "function_calling",
        "reasoning": "deep_reasoning",
        "math": "deep_reasoning",
        "proof": "deep_reasoning",
        "book": "long_context",
        "repository": "long_context"
    }

    def analyze(self, raw_request: str) -> ExtractedIntent:
        lower_req = raw_request.lower()
        required_caps = set()
        
        # 1. Extract capabilities from request heuristics
        for kw, cap in self.CAPABILITY_KEYWORD_MAP.items():
            if kw in lower_req:
                required_caps.add(cap)

        # 2. Estimate Task Category
        category = TaskCategory.WRITING
        if any(k in lower_req for k in ["code", "python", "bug", "function", "api", "react"]):
            category = TaskCategory.PROGRAMMING
        elif any(k in lower_req for k in ["paper", "research", "study", "analyze", "data"]):
            category = TaskCategory.RESEARCH
        elif any(k in lower_req for k in ["security", "vulnerability", "audit", "exploit"]):
            category = TaskCategory.CYBERSECURITY

        # 3. Detect Ambiguity & Missing Fields
        missing_fields = []
        ambiguities = []
        confidence = 0.90

        if "json_mode" in required_caps or "structured_output" in required_caps:
            if "schema" not in lower_req and "keys" not in lower_req:
                missing_fields.append("output_schema")
                ambiguities.append("User requested JSON output but did not provide key structure or schema.")
                confidence -= 0.20

        if len(raw_request.split()) < 8:
            ambiguities.append("User prompt is extremely brief and lacks situational context.")
            confidence -= 0.25

        return ExtractedIntent(
            raw_prompt=raw_request,
            primary_objective=raw_request,
            category=category,
            required_capabilities=list(required_caps),
            estimated_context_tokens=100000 if "long_context" in required_caps else 8000,
            extracted_constraints=[],
            confidence_score=max(0.10, confidence),
            missing_fields=missing_fields,
            detected_ambiguities=ambiguities
        )