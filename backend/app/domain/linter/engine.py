from app.domain.linter.base_models import LintResult, Severity
from app.domain.models.specification import TaskSpecification
from app.application.linter.rules.role_rule import RoleAssignmentRule
from app.application.linter.rules.format_rule import AmbiguousFormatRule

class PromptLinter:
    def __init__(self):
        # In a real app, these are injected or discovered dynamically
        self.rules = [
            RoleAssignmentRule(),
            AmbiguousFormatRule()
        ]

    def lint(self, spec: TaskSpecification) -> LintResult:
        result = LintResult()
        
        for rule in self.rules:
            warning = rule.evaluate(spec)
            if warning:
                result.warnings.append(warning)
                
                # Adjust score
                if warning.severity == Severity.ERROR:
                    result.is_valid = False
                    result.score -= 20
                elif warning.severity == Severity.WARNING:
                    result.score -= 10
                    
        return result