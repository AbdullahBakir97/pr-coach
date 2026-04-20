"""Domain entities for PR Coach."""

from __future__ import annotations

from dataclasses import dataclass, field

from .enums import CheckConclusion, PRSize, QualityLevel

__all__ = ["CheckResult", "PRAnalysis"]


@dataclass(slots=True)
class CheckResult:
    """Result of a single quality check."""

    name: str
    passed: bool
    message: str
    weight: int = 10


@dataclass(slots=True)
class PRAnalysis:
    """Complete analysis result for a pull request."""

    pr_number: int
    title: str
    score: int  # 0-100
    quality_level: QualityLevel
    pr_size: PRSize
    conclusion: CheckConclusion
    checks: list[CheckResult] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    lines_added: int = 0
    lines_removed: int = 0
    files_changed: int = 0

    @property
    def passed(self) -> bool:
        """Whether the PR passed the quality check."""
        return self.conclusion == CheckConclusion.SUCCESS

    @property
    def total_lines(self) -> int:
        """Total lines changed (added + removed)."""
        return self.lines_added + self.lines_removed

    @property
    def passed_checks(self) -> int:
        """Number of checks that passed."""
        return sum(1 for c in self.checks if c.passed)

    @property
    def total_checks(self) -> int:
        """Total number of checks run."""
        return len(self.checks)
