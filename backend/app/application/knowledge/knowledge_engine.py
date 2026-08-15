from typing import List
from app.domain.knowledge.interfaces import KnowledgeRepository
from app.domain.models.specification import TaskSpecification

class KnowledgeEngine:
    def __init__(self, repository: KnowledgeRepository):
        self.repository = repository

    def enrich_specification(self, spec: TaskSpecification, provider_name: str) -> TaskSpecification:
        """Dynamically injects provider best practices into the constraints."""
        
        # E.g., Query Qdrant for "anthropic coding best practices json format"
        query = f"{provider_name} best practices for {spec.category.value}"
        best_practices = self.repository.search(query, top_k=2)
        
        for practice in best_practices:
            # We tag these so the user knows they were system-injected
            spec.constraints.append(f"[Auto-Injected {provider_name} Rule] {practice.content}")
            
        return spec