"""Builds GitHub Check Run output from PR analysis results."""

from __future__ import annotations

from src.domain.entities import PRAnalysis

__all__ = ["CheckBuilder"]


class CheckBuilder:
    """Builds GitHub Check Run title, summary, and conclusion from analysis.

    Maps quality levels to appropriate check conclusions and generates
    human-readable summaries.
    """

    def build_title(self, analysis: PRAnalysis) -> str:
        """Build the check run title.

        Args:
            analysis: The completed PR analysis.

        Returns:
            A short title string for the check run.
        """
        return (
            f"PR Quality: {analysis.score}/100 "
            f"({analysis.quality_level.value.capitalize()}) - "
            f"{analysis.passed_checks}/{analysis.total_checks} checks passed"
        )

    def build_summary(self, analysis: PRAnalysis) -> str:
        """Build the check run summary in Markdown.

        Args:
            analysis: The completed PR analysis.

        Returns:
            A Markdown summary for the check run output.
        """
        lines: list[str] = []
        lines.append(f"## PR Quality Score: {analysis.score}/100")
        lines.append("")
        lines.append(f"**Level:** {analysis.quality_level.value.capitalize()}")
        lines.append(
            f"**Size:** {analysis.pr_size.value.upper()} "
            f"({analysis.lines_added}+ / {analysis.lines_removed}- across "
            f"{analysis.files_changed} files)"
        )
        lines.append("")

        lines.append("### Check Results")
        lines.append("")
        for check in analysis.checks:
            icon = "\u2705" if check.passed else "\u274c"
            name = check.name.replace("_", " ").title()
            lines.append(f"- {icon} **{name}**: {check.message}")
        lines.append("")

        failed = [c for c in analysis.checks if not c.passed]
        if failed:
            lines.append("### Improvements Needed")
            lines.append("")
            for check in failed:
                lines.append(f"- {check.message}")

        return "\n".join(lines)

    def build_conclusion(self, analysis: PRAnalysis) -> str:
        """Build the check conclusion string.

        Args:
            analysis: The completed PR analysis.

        Returns:
            A conclusion string: 'success', 'neutral', or 'failure'.
        """
        return analysis.conclusion.value
