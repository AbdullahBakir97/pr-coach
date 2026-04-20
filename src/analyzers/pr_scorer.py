"""PR quality scorer -- aggregates check results into a 0-100 score."""

from __future__ import annotations

from src.domain.entities import CheckResult
from src.domain.enums import CheckConclusion, QualityLevel

__all__ = ["PRScorer"]

# Weight assignments for each check category
_WEIGHTS: dict[str, int] = {
    "title_length": 8,
    "title_specificity": 7,
    "title_conventional": 5,
    "description_presence": 15,
    "description_sections": 8,
    "linked_issues": 10,
    "test_mention": 10,
    "screenshots": 5,
    "breaking_changes": 5,
    "checklist_completion": 7,
    "pr_size": 10,
    "file_count": 5,
    "single_focus": 7,
    "test_files": 8,
}


class PRScorer:
    """Aggregates all check results into a final PR quality score.

    Each check has a weight. The score is the sum of weights for passed
    checks divided by the total possible weight, scaled to 0-100.
    """

    def __init__(self, min_score: int = 60) -> None:
        self._min_score = min_score

    def score(self, check_results: list[tuple[str, bool, str]]) -> tuple[int, list[CheckResult]]:
        """Calculate the overall PR quality score.

        Args:
            check_results: List of (name, passed, message) tuples from analyzers.

        Returns:
            A tuple of (score, list of CheckResult entities).
        """
        checks: list[CheckResult] = []
        earned = 0
        total = 0

        for name, passed, message in check_results:
            weight = _WEIGHTS.get(name, 5)
            checks.append(CheckResult(name=name, passed=passed, message=message, weight=weight))
            total += weight
            if passed:
                earned += weight

        score = round((earned / max(total, 1)) * 100)
        return score, checks

    def determine_quality_level(self, score: int) -> QualityLevel:
        """Map a numeric score to a quality level.

        Args:
            score: The PR quality score (0-100).

        Returns:
            The corresponding QualityLevel.
        """
        if score >= 90:
            return QualityLevel.EXCELLENT
        if score >= 70:
            return QualityLevel.GOOD
        if score >= 50:
            return QualityLevel.FAIR
        if score >= 30:
            return QualityLevel.POOR
        return QualityLevel.FAILING

    def determine_conclusion(self, score: int) -> CheckConclusion:
        """Map a score to a GitHub Check conclusion.

        Args:
            score: The PR quality score (0-100).

        Returns:
            The corresponding CheckConclusion.
        """
        if score >= self._min_score:
            return CheckConclusion.SUCCESS
        if score >= self._min_score - 20:
            return CheckConclusion.NEUTRAL
        return CheckConclusion.FAILURE
