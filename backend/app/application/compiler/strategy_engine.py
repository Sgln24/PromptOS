from app.domain.models.specification import TaskSpecification, TaskCategory, PromptStrategy

class StrategyEngine:
    def apply_strategy(self, spec: TaskSpecification) -> TaskSpecification:
        """Enriches the specification with the optimal prompting strategy."""
        
        if spec.category in [TaskCategory.PROGRAMMING, TaskCategory.DATA_SCIENCE]:
            spec.strategy_applied = PromptStrategy.CHAIN_OF_THOUGHT
            spec.constraints.append("Think step-by-step before outputting final code.")
            
        elif spec.category == TaskCategory.RESEARCH:
            spec.strategy_applied = PromptStrategy.REACT
            spec.constraints.append("Use tools to verify claims before concluding.")
            
        elif len(spec.examples) > 0:
            spec.strategy_applied = PromptStrategy.FEW_SHOT
            
        else:
            spec.strategy_applied = PromptStrategy.DIRECT
            
        return spec