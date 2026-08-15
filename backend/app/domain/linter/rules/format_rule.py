# app/application/linter/rules/format_rule.py
class AmbiguousFormatRule:
    rule_id = "prompt-safety/ambiguous-format"

    def evaluate(self, spec: TaskSpecification) -> LintWarning | None:
        format_words = ["json", "xml", "csv", "markdown", "table"]
        objective_lower = spec.primary_objective.lower()
        
        mentions_format = any(word in objective_lower for word in format_words)
        
        if mentions_format and not spec.output_format:
            return LintWarning(
                rule_id=self.rule_id,
                severity=Severity.ERROR,
                message="Objective mentions a structured format, but no formal Output Schema is defined in the specification.",
                suggestion="Add an explicit 'output_format' schema to enforce structural boundaries."
            )
        return None