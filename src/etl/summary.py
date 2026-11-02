from dataclasses import dataclass, field


@dataclass
class RunSummary:
    """Collect the results of one pipeline run."""

    source: str
    extracted: int = 0
    valid: int = 0
    rejected: int = 0
    loaded: int = 0
    errors: list[str] = field(default_factory=list)

    def report(self) -> str:
        status = "FAILED" if self.errors else "SUCCESS"

        lines = [
            f"Pipeline: {self.source}",
            f"Status: {status}",
            f"Extracted: {self.extracted}",
            f"Valid: {self.valid}",
            f"Rejected: {self.rejected}",
            f"Loaded: {self.loaded}",
        ]

        if self.errors:
            lines.append("Errors:")
            lines.extend(f"  - {error}" for error in self.errors)

        return "\n".join(lines)