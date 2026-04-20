"""Unit tests for PRScorer."""

from __future__ import annotations

import pytest

from src.analyzers.pr_scorer import PRScorer
from src.domain.enums import CheckConclusion, QualityLevel


@pytest.fixture()
def scorer() -> PRScorer:
    """Create a PRScorer with default settings."""
    return PRScorer(min_score=60)


class TestScoring:
    """Tests for score calculation."""

    def test_all_checks_pass(self, scorer: PRScorer) -> None:
        """When all checks pass, score should be 100."""
        checks = [
            ("title_length", True, "Good"),
            ("title_specificity", True, "Good"),
            ("description_presence", True, "Good"),
            ("linked_issues", True, "Good"),
            ("test_mention", True, "Good"),
        ]
        score, results = scorer.score(checks)
        assert score == 100
        assert all(r.passed for r in results)

    def test_all_checks_fail(self, scorer: PRScorer) -> None:
        """When all checks fail, score should be 0."""
        checks = [
            ("title_length", False, "Bad"),
            ("title_specificity", False, "Bad"),
            ("description_presence", False, "Bad"),
            ("linked_issues", False, "Bad"),
        ]
        score, results = scorer.score(checks)
        assert score == 0
        assert not any(r.passed for r in results)

    def test_mixed_checks(self, scorer: PRScorer) -> None:
        """Mixed checks produce a score between 0 and 100."""
        checks = [
            ("title_length", True, "Good"),
            ("title_specificity", True, "Good"),
            ("description_presence", False, "Bad"),
            ("linked_issues", False, "Bad"),
            ("test_mention", True, "Good"),
        ]
        score, results = scorer.score(checks)
        assert 0 < score < 100

    def test_empty_checks(self, scorer: PRScorer) -> None:
        """Empty checks produce a score of 0."""
        score, results = scorer.score([])
        assert score == 0
        assert results == []

    def test_weights_applied(self, scorer: PRScorer) -> None:
        """Higher-weight checks impact score more."""
        # description_presence has weight 15, title_conventional has weight 5
        checks_high = [("description_presence", True, "Good"), ("title_conventional", False, "Bad")]
        checks_low = [("description_presence", False, "Bad"), ("title_conventional", True, "Good")]

        score_high, _ = scorer.score(checks_high)
        score_low, _ = scorer.score(checks_low)
        assert score_high > score_low


class TestQualityLevel:
    """Tests for quality level determination."""

    def test_excellent(self, scorer: PRScorer) -> None:
        """Score 90+ maps to excellent."""
        assert scorer.determine_quality_level(95) == QualityLevel.EXCELLENT

    def test_good(self, scorer: PRScorer) -> None:
        """Score 70-89 maps to good."""
        assert scorer.determine_quality_level(75) == QualityLevel.GOOD

    def test_fair(self, scorer: PRScorer) -> None:
        """Score 50-69 maps to fair."""
        assert scorer.determine_quality_level(55) == QualityLevel.FAIR

    def test_poor(self, scorer: PRScorer) -> None:
        """Score 30-49 maps to poor."""
        assert scorer.determine_quality_level(35) == QualityLevel.POOR

    def test_failing(self, scorer: PRScorer) -> None:
        """Score 0-29 maps to failing."""
        assert scorer.determine_quality_level(20) == QualityLevel.FAILING


class TestConclusion:
    """Tests for check conclusion determination."""

    def test_success(self, scorer: PRScorer) -> None:
        """Score at or above min_score produces success."""
        assert scorer.determine_conclusion(60) == CheckConclusion.SUCCESS
        assert scorer.determine_conclusion(100) == CheckConclusion.SUCCESS

    def test_neutral(self, scorer: PRScorer) -> None:
        """Score within 20 below min_score produces neutral."""
        assert scorer.determine_conclusion(45) == CheckConclusion.NEUTRAL
        assert scorer.determine_conclusion(59) == CheckConclusion.NEUTRAL

    def test_failure(self, scorer: PRScorer) -> None:
        """Score more than 20 below min_score produces failure."""
        assert scorer.determine_conclusion(30) == CheckConclusion.FAILURE
        assert scorer.determine_conclusion(0) == CheckConclusion.FAILURE
