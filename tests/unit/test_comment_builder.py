"""Tests for the contextual, severity-aware PR Coach comment builder."""

from __future__ import annotations

from typing import ClassVar

import pytest

from src.domain.entities import CheckResult, PRAnalysis
from src.domain.enums import CheckConclusion, PRSize, QualityLevel
from src.generators.comment_builder import CommentBuilder

# ------------------------------------------------------------------ #
# Helpers
# ------------------------------------------------------------------ #


@pytest.fixture
def builder() -> CommentBuilder:
    return CommentBuilder()


def _check(name: str, passed: bool, message: str = "") -> CheckResult:
    return CheckResult(name=name, passed=passed, message=message or f"{name} message")


def _analysis(
    *,
    score: int = 90,
    quality: QualityLevel = QualityLevel.EXCELLENT,
    conclusion: CheckConclusion = CheckConclusion.SUCCESS,
    checks: list[CheckResult] | None = None,
    pr_size: PRSize = PRSize.SMALL,
    lines_added: int = 50,
    lines_removed: int = 10,
    files_changed: int = 3,
) -> PRAnalysis:
    return PRAnalysis(
        pr_number=42,
        title="feat(auth): add OAuth login",
        score=score,
        quality_level=quality,
        pr_size=pr_size,
        conclusion=conclusion,
        checks=checks
        or [
            _check("title_length", True),
            _check("description_presence", True),
            _check("linked_issues", True),
        ],
        suggestions=[],
        lines_added=lines_added,
        lines_removed=lines_removed,
        files_changed=files_changed,
    )


# ------------------------------------------------------------------ #
# Scenario 1: Excellent PR — concise, encouraging
# ------------------------------------------------------------------ #


class TestExcellentPR:
    def test_uses_green_indicator(self, builder):
        comment = builder.build(_analysis(quality=QualityLevel.EXCELLENT))
        assert "🟢" in comment

    def test_no_failed_section(self, builder):
        comment = builder.build(_analysis(quality=QualityLevel.EXCELLENT))
        assert "What to address" not in comment

    def test_no_tip_when_nothing_failed(self, builder):
        comment = builder.build(_analysis(quality=QualityLevel.EXCELLENT))
        assert "**Tip:**" not in comment

    def test_summary_table_shows_full_stats(self, builder):
        analysis = _analysis(
            score=95,
            quality=QualityLevel.EXCELLENT,
            pr_size=PRSize.SMALL,
            lines_added=80,
            lines_removed=20,
            files_changed=4,
        )
        comment = builder.build(analysis)
        assert "95/100" in comment
        assert "Excellent" in comment
        assert "80+" in comment
        assert "20-" in comment
        assert "4 files" in comment


# ------------------------------------------------------------------ #
# Scenario 2: Failing PR — every failed check gets specific advice
# ------------------------------------------------------------------ #


class TestFailingPR:
    def test_uses_red_indicator(self, builder):
        analysis = _analysis(
            score=20,
            quality=QualityLevel.FAILING,
            conclusion=CheckConclusion.FAILURE,
            checks=[
                _check("description_presence", False),
                _check("linked_issues", False),
                _check("test_files", False),
            ],
        )
        comment = builder.build(analysis)
        assert "🔴" in comment

    def test_each_failed_check_has_specific_advice(self, builder):
        analysis = _analysis(
            score=20,
            quality=QualityLevel.FAILING,
            conclusion=CheckConclusion.FAILURE,
            checks=[
                _check("description_presence", False),
                _check("linked_issues", False),
                _check("test_files", False),
            ],
        )
        comment = builder.build(analysis)

        # Each check has a specific, actionable advice string
        assert "what changed" in comment.lower()
        assert "Closes #N" in comment
        assert "test file" in comment.lower()

    def test_pr_size_advice_mentions_splitting(self, builder):
        analysis = _analysis(
            score=30,
            quality=QualityLevel.POOR,
            conclusion=CheckConclusion.FAILURE,
            pr_size=PRSize.XL,
            lines_added=2000,
            lines_removed=500,
            files_changed=45,
            checks=[
                _check("pr_size", False, "PR is too large"),
                _check("file_count", False, "Too many files"),
            ],
        )
        comment = builder.build(analysis)

        assert "splitting" in comment.lower() or "split" in comment.lower()
        assert "500 lines" in comment

    def test_title_convention_advice_lists_allowed_types(self, builder):
        analysis = _analysis(
            score=40,
            quality=QualityLevel.POOR,
            conclusion=CheckConclusion.FAILURE,
            checks=[_check("title_conventional", False)],
        )
        comment = builder.build(analysis)
        assert "feat, fix, docs" in comment
        assert "type(scope): description" in comment


# ------------------------------------------------------------------ #
# Scenario 3: Mixed — some failed, some passed
# ------------------------------------------------------------------ #


class TestMixedPR:
    def test_passed_summary_lists_at_most_three_then_count(self, builder):
        passing = [_check(f"check_{i}", True) for i in range(7)]
        failing = [_check("description_presence", False)]
        analysis = _analysis(
            score=60,
            quality=QualityLevel.FAIR,
            conclusion=CheckConclusion.NEUTRAL,
            checks=passing + failing,
        )
        comment = builder.build(analysis)

        assert "What's already good" in comment
        # 7 passed, so the summary should show "and 4 more"
        assert "4 more" in comment

    def test_passed_summary_lists_all_when_three_or_fewer(self, builder):
        analysis = _analysis(
            score=70,
            quality=QualityLevel.GOOD,
            conclusion=CheckConclusion.SUCCESS,
            checks=[
                _check("title_length", True),
                _check("description_presence", True),
                _check("linked_issues", True),
            ],
        )
        comment = builder.build(analysis)

        assert "title length" in comment
        assert "description presence" in comment
        assert "linked issues" in comment

    def test_only_failed_checks_get_advice_blocks(self, builder):
        analysis = _analysis(
            score=60,
            quality=QualityLevel.FAIR,
            conclusion=CheckConclusion.NEUTRAL,
            checks=[
                _check("title_length", True),  # passed
                _check("linked_issues", False),  # failed
            ],
        )
        comment = builder.build(analysis)

        assert "Linked Issues" in comment  # appears in advice section
        # Title Length is passed, should only appear in the "What's already good"
        # summary, not as a header in "What to address".
        assert "**Title Length**" not in comment


# ------------------------------------------------------------------ #
# Scenario 4: Contextual tip selection
# ------------------------------------------------------------------ #


class TestContextualTip:
    def test_tip_relates_to_what_actually_failed(self, builder):
        # Only PR size fails — tip should be about size, not random
        analysis = _analysis(
            score=50,
            quality=QualityLevel.POOR,
            conclusion=CheckConclusion.FAILURE,
            checks=[_check("pr_size", False)],
            pr_size=PRSize.XL,
        )
        comment = builder.build(analysis)
        assert "**Tip:**" in comment
        assert "400 lines" in comment

    def test_test_files_failure_picks_test_tip(self, builder):
        analysis = _analysis(
            score=40,
            quality=QualityLevel.POOR,
            conclusion=CheckConclusion.FAILURE,
            checks=[_check("test_files", False)],
        )
        comment = builder.build(analysis)
        assert "Tests are documentation" in comment

    def test_no_tip_when_no_relevant_failure_match(self, builder):
        # Failure doesn't match any tip key — no tip section.
        analysis = _analysis(
            score=50,
            quality=QualityLevel.FAIR,
            conclusion=CheckConclusion.NEUTRAL,
            checks=[_check("some_unmapped_check", False)],
        )
        comment = builder.build(analysis)
        assert "**Tip:**" not in comment


# ------------------------------------------------------------------ #
# Scenario 5: Voice quality — no AI prose
# ------------------------------------------------------------------ #


class TestVoiceQuality:
    AI_TRIGGERS: ClassVar[list[str]] = [
        "I'd be happy to",
        "hope this helps",
        "feel free to reach out",
        "delve into",
        "holistic approach",
        "in conclusion",
        "let me know if you",
    ]

    def test_no_ai_phrases_in_prose(self, builder):
        analysis = _analysis(
            score=30,
            quality=QualityLevel.POOR,
            conclusion=CheckConclusion.FAILURE,
            checks=[
                _check("description_presence", False),
                _check("linked_issues", False),
                _check("test_files", False),
                _check("pr_size", False),
            ],
        )
        comment = builder.build(analysis)
        lowered = comment.lower()

        for phrase in self.AI_TRIGGERS:
            assert phrase.lower() not in lowered, f"Comment contains AI-style phrase '{phrase}'"

    def test_uses_imperative_advice(self, builder):
        analysis = _analysis(
            score=30,
            quality=QualityLevel.POOR,
            conclusion=CheckConclusion.FAILURE,
            checks=[
                _check("description_presence", False),
                _check("linked_issues", False),
                _check("screenshots", False),
            ],
        )
        comment = builder.build(analysis)

        imperatives = ["Add", "Link", "Attach", "Use", "Note", "Mention", "Tick"]
        found = [v for v in imperatives if v in comment]
        assert len(found) >= 2, f"Expected imperative verbs, found only {found}"


# ------------------------------------------------------------------ #
# Scenario 6: Footer
# ------------------------------------------------------------------ #


class TestFooter:
    def test_footer_links_to_project(self, builder):
        comment = builder.build(_analysis())
        assert "github.com/AbdullahBakir97/pr-coach" in comment
