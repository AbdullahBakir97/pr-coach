"""PR diff quality analyzer."""

from __future__ import annotations

import re

from src.domain.enums import PRSize

__all__ = ["DiffAnalyzer"]

_TEST_FILE_RE = re.compile(
    # Match common test file patterns across languages and monorepo layouts.
    # Includes singular 'test/' and plural 'tests/', plus workspace-nested paths
    # like 'packages/foo/test/' or 'packages/foo/__tests__/'.
    r"(?:"
    r"test_|_test\.|\.test\.|\.spec\.|"  # name patterns: test_x, x_test., x.test., x.spec.
    r"(?:^|/)tests?/|"  # /test/ or /tests/ anywhere in path
    r"(?:^|/)__tests__/|"  # /__tests__/ anywhere
    r"(?:^|/)spec/|"  # /spec/ anywhere
    r"(?:^|/)testing/|"  # /testing/ (some Python projects)
    r"\.test\.t?sx?$|\.spec\.t?sx?$"  # .test.ts/.test.tsx/.spec.ts/.spec.tsx
    r")",
    re.IGNORECASE,
)

_MAX_FILES_DEFAULT = 20
_MAX_LINES_DEFAULT = 500


class DiffAnalyzer:
    """Checks PR diff for size, file count, and test coverage signals.

    Evaluates:
    - PR size (lines changed)
    - File count
    - Single-purpose (heuristic)
    - Test files included
    """

    def __init__(self, max_files: int = _MAX_FILES_DEFAULT, max_lines: int = _MAX_LINES_DEFAULT) -> None:
        self._max_files = max_files
        self._max_lines = max_lines

    def analyze(
        self,
        diff: str,
        files: list[dict[str, object]],
    ) -> list[tuple[str, bool, str]]:
        """Analyze the PR diff for size and quality signals.

        Args:
            diff: The raw diff text.
            files: List of file dicts with filename, additions, deletions.

        Returns:
            A list of (check_name, passed, message) tuples.
        """
        results: list[tuple[str, bool, str]] = []

        # Calculate totals
        total_additions = sum(int(f.get("additions", 0)) for f in files)
        total_deletions = sum(int(f.get("deletions", 0)) for f in files)
        total_lines = total_additions + total_deletions
        file_count = len(files)
        filenames = [str(f.get("filename", "")) for f in files]

        # PR size check
        pr_size = self._classify_size(total_lines)
        if total_lines <= self._max_lines:
            results.append(("pr_size", True, f"PR size is manageable ({total_lines} lines, {pr_size.value})"))
        else:
            results.append(
                (
                    "pr_size",
                    False,
                    f"PR is too large ({total_lines} lines, {pr_size.value}) -- consider splitting",
                )
            )

        # File count check
        if file_count <= self._max_files:
            results.append(("file_count", True, f"Reasonable file count ({file_count} files)"))
        else:
            results.append(("file_count", False, f"Too many files changed ({file_count}) -- consider splitting the PR"))

        # Single focus heuristic
        directories = set()
        for fname in filenames:
            parts = fname.split("/")
            if len(parts) > 1:
                directories.add(parts[0])
        if len(directories) <= 3 or file_count <= 5:
            results.append(("single_focus", True, "PR appears focused on a single concern"))
        else:
            results.append(
                (
                    "single_focus",
                    False,
                    f"PR touches {len(directories)} top-level directories -- may lack focus",
                )
            )

        # Test files included
        test_files = [f for f in filenames if _TEST_FILE_RE.search(f)]
        source_files = [f for f in filenames if not _TEST_FILE_RE.search(f)]
        if test_files:
            results.append(("test_files", True, f"Includes {len(test_files)} test file(s)"))
        elif source_files:
            results.append(("test_files", False, "No test files included -- consider adding tests"))
        else:
            results.append(("test_files", True, "No source files to test"))

        return results

    @staticmethod
    def _classify_size(total_lines: int) -> PRSize:
        """Classify PR size based on total lines changed.

        Args:
            total_lines: Total lines added + removed.

        Returns:
            A PRSize enum value.
        """
        if total_lines < 10:
            return PRSize.XS
        if total_lines < 100:
            return PRSize.SMALL
        if total_lines < 500:
            return PRSize.MEDIUM
        if total_lines < 1000:
            return PRSize.LARGE
        return PRSize.XL
