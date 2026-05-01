"""Builds Markdown coaching comments for pull requests.

The comment is designed to feel like a senior reviewer wrote it: tone scales
with severity, advice is specific per failed check, and the closing tip is
contextual to what's actually missing — not a random generic platitude.
"""

from __future__ import annotations

from src.domain.entities import CheckResult, PRAnalysis
from src.domain.enums import QualityLevel

__all__ = ["CommentBuilder"]


# Per-check actionable advice. Keys match the CheckResult.name produced by
# the analyzers; each value is the concrete next step a contributor can take.
# When a check fails, the contributor sees a tailored block instead of
# the bare check message.
_CHECK_ADVICE: dict[str, str] = {
    "title_length": (
        "Aim for 20-72 characters. Long enough to convey the change, short enough to fit in a one-line PR list."
    ),
    "title_specificity": (
        "Vague titles like 'fix' or 'update' are hard to triage. "
        "Mention the component and the action — e.g. `fix(auth): handle null email on submit`."
    ),
    "title_conventional": (
        "Use conventional commit format: `type(scope): description`. "
        "Examples: `feat(api): add /v2/search`, `fix(auth): resolve race condition on logout`. "
        "Allowed types: feat, fix, docs, style, refactor, perf, test, build, ci, chore."
    ),
    "description_presence": (
        "PRs without a description force reviewers to read the diff cold. Add at least: (a) what changed and (b) why."
    ),
    "description_sections": (
        "Add `## What` and `## Why` sections. Reviewers can skim a structured PR in 30 seconds; "
        "an unstructured one takes minutes."
    ),
    "linked_issues": (
        "Link the issue this PR resolves with `Closes #N`, `Fixes #N`, or `Resolves #N`. "
        "GitHub will auto-close the issue on merge and threads stay navigable."
    ),
    "test_mention": (
        "Note how this was tested: which test file covers it, or what manual steps you ran. "
        "If existing tests cover it, mention which ones — reviewers shouldn't have to guess."
    ),
    "screenshots": (
        "Attach a screenshot or screen recording. UI PRs without visuals get stuck "
        "in the review queue while reviewers ask for them."
    ),
    "breaking_changes": (
        "This PR removes or changes a public API. Add a `BREAKING CHANGE:` note explaining "
        "what breaks and how consumers should migrate."
    ),
    "checklist_completion": (
        "Tick off the checklist items. Unchecked items either need to be done, "
        "removed from the template, or moved to a follow-up issue."
    ),
    "pr_size": (
        "PRs over 500 lines are 3x harder to review. Consider splitting by concern: "
        "(1) refactor PR, (2) feature PR, (3) tests/docs PR. Smaller PRs get reviewed faster."
    ),
    "file_count": (
        "PRs touching 20+ files are usually safer to split. Group changes by directory or "
        "feature area into separate PRs."
    ),
    "single_focus": (
        "This PR touches multiple unrelated directories. Single-purpose PRs are easier to "
        "review, revert, and attribute in the changelog."
    ),
    "test_files": (
        "The diff modifies source files but no tests changed. If existing tests cover this, "
        "mention which file. Otherwise, this is the right time to add tests."
    ),
}


# Closing tips chosen contextually based on the check that failed most heavily.
# Selected by the *first* failure key found in this list — order matters.
_CONTEXTUAL_TIPS: list[tuple[str, str]] = [
    ("pr_size", "Aim for PRs under 400 lines. Reviewers stay sharper, regressions are caught faster."),
    ("file_count", "Touching many files? Consider a 'preparatory refactor' PR followed by the feature PR."),
    ("test_files", "Tests are documentation that runs. Even one test for the happy path makes review easier."),
    ("description_presence", "A 3-line PR description saves a 10-message back-and-forth in review."),
    ("description_sections", "Reviewers read 'What' and 'Why' first. Lead with those, save 'How' for the diff."),
    ("linked_issues", "Linked PRs build a searchable history of *why* the project evolved the way it did."),
    ("screenshots", "Even a 5-second Loom video saves a reviewer from cloning to verify."),
    ("title_conventional", "Conventional commits enable auto-generated changelogs and clear release notes."),
    ("title_specificity", "Specific titles let triagers route the PR to the right reviewer in seconds."),
]


class CommentBuilder:
    """Builds a Markdown coaching comment from a PR analysis."""

    def build(self, analysis: PRAnalysis) -> str:
        """Build the full coaching comment.

        Args:
            analysis: The completed PR analysis.

        Returns:
            A Markdown string ready to post as a GitHub comment.
        """
        sections: list[str] = [
            self._header(analysis),
            self._summary_table(analysis),
        ]

        failed = [c for c in analysis.checks if not c.passed]
        if failed:
            sections.append(self._failed_section(failed, analysis))

        # Compact roll-up of what passed — keeps the comment honest about
        # what's already good without bloating it.
        if any(c.passed for c in analysis.checks):
            sections.append(self._passed_summary(analysis))

        sections.append(self._footer(failed))
        return "\n\n".join(sections)

    # ------------------------------------------------------------------ #
    # Sections
    # ------------------------------------------------------------------ #

    @staticmethod
    def _header(analysis: PRAnalysis) -> str:
        """Header with a tone that scales with severity."""
        passed = analysis.passed_checks
        total = analysis.total_checks

        if analysis.quality_level == QualityLevel.EXCELLENT:
            indicator = "🟢"
            opener = (
                f"This PR is well-formed — {passed}/{total} checks pass and the structure makes review straightforward."
            )
        elif analysis.quality_level == QualityLevel.GOOD:
            indicator = "🟢"
            opener = (
                f"Solid PR — {passed}/{total} checks pass. A couple of minor items below if you want to polish further."
            )
        elif analysis.quality_level == QualityLevel.FAIR:
            indicator = "🟡"
            opener = (
                f"This PR can be reviewed, but {total - passed} item(s) below would speed it up "
                "and reduce back-and-forth."
            )
        elif analysis.quality_level == QualityLevel.POOR:
            indicator = "🟠"
            opener = (
                f"This PR is missing several things reviewers need ({passed}/{total} checks pass). "
                "Addressing the items below will make it much easier to review."
            )
        else:  # FAILING
            indicator = "🔴"
            opener = (
                f"Only {passed}/{total} checks pass. Reviewers will likely ask for the items below "
                "before engaging — fixing them now saves time on both sides."
            )

        return f"## {indicator} PR Coach\n\n{opener}"

    @staticmethod
    def _summary_table(analysis: PRAnalysis) -> str:
        """Compact stats table at the top of the comment."""
        size_label = analysis.pr_size.value.upper()
        return (
            "| Metric | Value |\n"
            "| --- | --- |\n"
            f"| Quality | **{analysis.score}/100** ({analysis.quality_level.value.title()}) |\n"
            f"| Checks | {analysis.passed_checks}/{analysis.total_checks} passing |\n"
            f"| Size | {size_label} ({analysis.lines_added}+ / {analysis.lines_removed}-, "
            f"{analysis.files_changed} files) |"
        )

    @staticmethod
    def _failed_section(failed: list[CheckResult], analysis: PRAnalysis) -> str:
        """Detailed advice for each failed check."""
        lines: list[str] = ["### What to address"]
        for check in failed:
            advice = _CHECK_ADVICE.get(check.name, check.message)
            friendly = check.name.replace("_", " ").title()
            lines.append(f"\n**{friendly}**")
            lines.append(advice)
            # If the check has its own detail message that adds info beyond
            # the generic advice, surface it as a sub-line.
            if check.message and check.message not in advice:
                lines.append(f"_Details: {check.message}_")
        return "\n".join(lines)

    @staticmethod
    def _passed_summary(analysis: PRAnalysis) -> str:
        """Brief one-liner crediting what's already good."""
        passed_names = [c.name.replace("_", " ") for c in analysis.checks if c.passed]
        if not passed_names:
            return ""

        if len(passed_names) <= 3:
            joined = ", ".join(passed_names)
            return f"### What's already good\n\n{joined}."

        # Show the first 3 then a count summary so the comment stays compact.
        first_three = ", ".join(passed_names[:3])
        rest = len(passed_names) - 3
        return f"### What's already good\n\n{first_three}, and {rest} more."

    @staticmethod
    def _footer(failed_checks: list[CheckResult]) -> str:
        """Footer with a contextual tip and link back to the project."""
        tip = ""
        if failed_checks:
            failed_names = {c.name for c in failed_checks}
            for key, message in _CONTEXTUAL_TIPS:
                if key in failed_names:
                    tip = f"> **Tip:** {message}\n\n"
                    break

        return (
            f"{tip}"
            "_[PR Coach](https://github.com/AbdullahBakir97/pr-coach) "
            "— PR quality coaching on every pull request_"
        )
