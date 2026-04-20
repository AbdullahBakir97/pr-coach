"""PR description quality analyzer."""

from __future__ import annotations

import re

__all__ = ["DescriptionAnalyzer"]

_ISSUE_RE = re.compile(
    r"(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+#\d+|#\d+|"
    r"https?://github\.com/[^/]+/[^/]+/issues/\d+",
    re.IGNORECASE,
)

_TEST_RE = re.compile(
    r"(?:test|tested|testing|spec|coverage|unit test|integration test|e2e)",
    re.IGNORECASE,
)

_SCREENSHOT_RE = re.compile(
    r"(?:!\[.*?\]\(.*?\)|<img\s|screenshot|screen\s*shot|recording|\.png|\.gif|\.jpg|\.mp4)",
    re.IGNORECASE,
)

_BREAKING_RE = re.compile(
    r"(?:breaking\s*change|BREAKING|backward.?incompatible|migration\s*required)",
    re.IGNORECASE,
)

_CHECKLIST_RE = re.compile(r"- \[[ x]\]", re.IGNORECASE)

_WHAT_WHY_RE = re.compile(
    r"(?:^##?\s*(?:what|why|summary|description|changes|motivation|context))",
    re.IGNORECASE | re.MULTILINE,
)


class DescriptionAnalyzer:
    """Checks PR description for completeness and quality signals.

    Evaluates:
    - Description presence and length
    - What/why sections
    - Linked issues
    - Test mentions
    - Screenshots (for UI changes)
    - Breaking change notes
    - Checklist completion
    """

    def analyze(self, body: str | None) -> list[tuple[str, bool, str]]:
        """Analyze a PR description for quality.

        Args:
            body: The pull request body/description text (may be None).

        Returns:
            A list of (check_name, passed, message) tuples.
        """
        results: list[tuple[str, bool, str]] = []

        if not body or not body.strip():
            results.append(("description_presence", False, "PR has no description"))
            results.append(("linked_issues", False, "No linked issues found"))
            results.append(("test_mention", False, "No mention of testing"))
            results.append(("checklist_completion", False, "No checklist found"))
            return results

        text = body.strip()

        # Description presence and quality
        if len(text) >= 50:
            results.append(("description_presence", True, "Description is detailed"))
        elif len(text) >= 20:
            results.append(("description_presence", True, "Description is present but could be more detailed"))
        else:
            results.append(("description_presence", False, "Description is too brief (less than 20 characters)"))

        # What/Why sections
        if _WHAT_WHY_RE.search(text):
            results.append(("description_sections", True, "Description has structured sections"))
        else:
            results.append(("description_sections", False, "Consider adding ## What / ## Why sections"))

        # Linked issues
        if _ISSUE_RE.search(text):
            results.append(("linked_issues", True, "PR references related issues"))
        else:
            results.append(("linked_issues", False, "No linked issues found -- link with 'Closes #123'"))

        # Test mentions
        if _TEST_RE.search(text):
            results.append(("test_mention", True, "Testing is mentioned"))
        else:
            results.append(("test_mention", False, "No mention of testing -- describe how this was tested"))

        # Screenshots
        if _SCREENSHOT_RE.search(text):
            results.append(("screenshots", True, "Screenshots/recordings included"))
        else:
            results.append(("screenshots", False, "No screenshots -- include them for UI changes"))

        # Breaking changes
        if _BREAKING_RE.search(text):
            results.append(("breaking_changes", True, "Breaking changes are documented"))

        # Checklist completion
        checklist_items = _CHECKLIST_RE.findall(text)
        if checklist_items:
            completed = sum(1 for item in re.findall(r"- \[x\]", text, re.IGNORECASE))
            total = len(checklist_items)
            if completed == total:
                results.append(("checklist_completion", True, f"Checklist complete ({completed}/{total})"))
            else:
                results.append(
                    ("checklist_completion", False, f"Checklist incomplete ({completed}/{total} items checked)")
                )
        else:
            results.append(("checklist_completion", False, "No checklist found -- consider adding one"))

        return results
