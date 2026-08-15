from pydantic import BaseModel
from typing import List, Optional
from app.application.intent.analyzer import ExtractedIntent

class ClarificationQuestion(BaseModel):
    id: str
    question: str
    rationale: str
    suggested_options: Optional[List[str]] = None

class ClarificationBatch(BaseModel):
    requires_user_input: bool
    confidence_score: float
    questions: List[ClarificationQuestion]

class RequirementGatherer:
    """
    Ensures PromptOS acts like a senior consultant: asking only high-value, minimal questions
    when intent confidence drops below threshold (0.80).
    """

    CONFIDENCE_THRESHOLD = 0.80

    def evaluate_and_gather(self, intent: ExtractedIntent) -> ClarificationBatch:
        if intent.confidence_score >= self.CONFIDENCE_THRESHOLD:
            return ClarificationBatch(
                requires_user_input=False,
                confidence_score=intent.confidence_score,
                questions=[]
            )

        questions = []
        
        if "output_schema" in intent.missing_fields:
            questions.append(ClarificationQuestion(
                id="q_output_schema",
                question="What specific fields or structure do you need in the JSON output?",
                rationale="Explicit schemas prevent hallucinated fields and formatting errors.",
                suggested_options=["Key-Value List", "Nested JSON Schema", "Array of Objects"]
            ))

        if "User prompt is extremely brief" in " ".join(intent.detected_ambiguities):
            questions.append(ClarificationQuestion(
                id="q_target_audience",
                question="Who is the target audience or what is the primary execution environment for this task?",
                rationale="Clarifying the role and scope produces drastically higher quality prompt constraints.",
                suggested_options=["Production Backend API", "Internal Team Tool", "Executive Summary"]
            ))

        return ClarificationBatch(
            requires_user_input=True,
            confidence_score=intent.confidence_score,
            questions=questions
        )