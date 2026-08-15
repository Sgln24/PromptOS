from pydantic import BaseModel
from typing import List
from enum import Enum
from app.domain.models.specification import TaskSpecification

class Severity(str, Enum):
    ERROR = "error"       # Will fail compilation
    WARNING = "warning"   # Hallucination risk or degraded performance
    INFO = "info"         # Optimization suggestion

class LintWarning(BaseModel):
    rule_id: str
    severity: Severity
    message: str
    suggestion: str

class LintResult(BaseModel):
    score: int = 100
    warnings: List[LintWarning] = []
    is_valid: bool = True