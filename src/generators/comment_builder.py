"""Builds markdown coaching comments for pull requests."""

from __future__ import annotations

from src.domain.entities import PRAnalysis
from src.domain.enums import QualityLevel

__all__ = ["CommentBuilder"]

_QUALITY_EMOJI: dict[QualityLevel, str] = {
    QualityLevel.EXCELLENT: "\u2728",
    QualityLevel.GOOD: "\u2705",
    QualityLevel.FAIR: "\u26a0\ufe0f",
    QualityLevel.POOR: "\u274c",
    QualityLevel.FAILING: "\U0001f6a8",
}

_TIPS: list[str] = [
    "Keep PRs small and focused on a single concern for faster reviews.",
    "Link related issues so reviewers understand the context.",
    "Include screenshots for any visual changes.",
    "Describe *what* changed and *why* -- not just *how*.",
    "Add a checklist to track sub-tasks within the PR.",
    "Mention how the change was tested to build reviewer confidence.",
    "Note any breaking changes prominently so downstream consumers are aware.",
]


class CommentBuilder:
    """Builds a structured Markdown coaching comment from analysis results.

    The comment includes a score badge, checks table, specific suggestions,
    and a rotating tip.
    """

    def build(self, analysis: PRAnalysis) -> str:
        """Build the full coaching comment.

        Args:
            analysis: The completed PR analysis.

        Returns:
            A Markdown string ready to post as a GitHub comment.
        """
        emoji = _QUALITY_EMOJI.get(analysis.quality_level, "")
        lines: list[str] = []

        lines.append("## PR Coach Report")
        lines.append("")
        lines.append(
            f"{emoji} **Score: {analysis.score}/100** "
            f"({analysis.quality_level.value.capitalize()}) | "
            f"{analysis.passed_checks}/{analysis.total_checks} checks passed"
        )
        lines.append("")

        # Checks table
        lines.append("### Checks")
        lines.append("")
        lines.append("| Check | Status | Details |")
        lines.append("|-------|--------|---------|")
        for check in analysis.checks:
            status = "\u2705" if check.passed else "\u274c"
            name = check.name.replace("_", " ").title()
            lines.append(f"| {name} | {status} | {check.message} |")
        lines.append("")

        # Suggestions
        failed_checks = [c for c in analysis.checks if not c.passed]
        if failed_checks:
            lines.append("### Suggestions")
            lines.append("")
            for check in failed_checks:
                lines.append(f"- {check.message}")
            lines.append("")

        # Additional suggestions
        if analysis.suggestions:
            for suggestion in analysis.suggestions:
                lines.append(f"- {suggestion}")
            lines.append("")

        # Tip
        tip_index = analysis.pr_number % len(_TIPS)
        lines.append("---")
        lines.append(f"> \U0001f4a1 **Tip:** {_TIPS[tip_index]}")
        lines.append("")
        lines.append(
            "*PR Coach helps you write better pull requests. [Learn more](https://github.com/AbdullahBakir97/pr-coach)*"
        )

        return "\n".join(lines)
