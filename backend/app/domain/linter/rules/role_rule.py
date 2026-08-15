# app/application/linter/rules/role_rule.py
from app.domain.linter.base_models import LintWarning, Severity
from app.domain.models.specification import TaskSpecification

class RoleAssignmentRule:
    rule_id = "prompt-style/missing-role"

    def evaluate(self, spec: TaskSpecification) -> LintWarning | None:
        if not spec.role_persona:
            return LintWarning(
                rule_id=self.rule_id,
                severity=Severity.WARNING,
                message="No role persona assigned.",
                suggestion="Define a specific expert persona (e.g., 'Senior Cloud Architect') to ground the model's vocabulary and reasoning."
            )
        return None

