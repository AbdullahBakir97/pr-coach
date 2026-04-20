"""PR title quality analyzer."""

from __future__ import annotations

import re

__all__ = ["TitleAnalyzer"]

_CONVENTIONAL_RE = re.compile(
    r"^(?:feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)"
    r"(?:\([^)]+\))?!?:\s+.+$",
    re.IGNORECASE,
)

_MIN_LENGTH = 10
_MAX_LENGTH = 72
_VAGUE_WORDS = {"update", "fix", "change", "stuff", "things", "misc", "wip", "temp"}


class TitleAnalyzer:
    """Checks PR title for length, specificity, and conventional format.

    Evaluates:
    - Title length (10-72 characters)
    - Specificity (no vague single-word titles)
    - Conventional commit format (optional bonus)
    """

    def analyze(self, title: str) -> list[tuple[str, bool, str]]:
        """Analyze a PR title for quality signals.

        Args:
            title: The pull request title string.

        Returns:
            A list of (check_name, passed, message) tuples.
        """
        results: list[tuple[str, bool, str]] = []

        # Length check
        length = len(title.strip())
        if length >= _MIN_LENGTH and length <= _MAX_LENGTH:
            results.append(("title_length", True, f"Title length is good ({length} chars)"))
        elif length < _MIN_LENGTH:
            results.append(("title_length", False, f"Title is too short ({length} chars, min {_MIN_LENGTH})"))
        else:
            results.append(("title_length", False, f"Title is too long ({length} chars, max {_MAX_LENGTH})"))

        # Specificity check
        words = title.strip().lower().split()
        if len(words) >= 3:
            results.append(("title_specificity", True, "Title is descriptive"))
        elif len(words) == 1 and words[0] in _VAGUE_WORDS:
            results.append(("title_specificity", False, f"Title is too vague: '{title.strip()}'"))
        elif len(words) < 3:
            results.append(("title_specificity", False, "Title should have at least 3 words for clarity"))
        else:
            results.append(("title_specificity", True, "Title is descriptive"))

        # Conventional format check (bonus, not required)
        if _CONVENTIONAL_RE.match(title.strip()):
            results.append(("title_conventional", True, "Title follows conventional commit format"))
        else:
            results.append(
                ("title_conventional", False, "Consider using conventional format: type(scope): description")
            )

        return results
