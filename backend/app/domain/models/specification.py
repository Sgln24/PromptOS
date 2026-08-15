from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from enum import Enum

class TaskCategory(str, Enum):
    PROGRAMMING = "programming"
    DATA_SCIENCE = "data_science"
    WRITING = "writing"
    RESEARCH = "research"
    CYBERSECURITY = "cybersecurity"
    # ... extensible list

class PromptStrategy(str, Enum):
    DIRECT = "direct"
    CHAIN_OF_THOUGHT = "chain_of_thought"
    FEW_SHOT = "few_shot"
    REACT = "react"
    TREE_OF_THOUGHTS = "tree_of_thoughts"

class TaskSpecification(BaseModel):
    category: str
    primary_objective: str
    role_persona: Optional[str] = None
    context_data: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    output_format: Optional[Dict[str, str]] = None  # e.g., JSON schema or description
    examples: List[Dict[str, str]] = Field(default_factory=list) # User/Assistant pairs
    strategy_applied: Optional[PromptStrategy] = None