"""Abstract interfaces for PR Coach services."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

__all__ = [
    "ITitleAnalyzer",
    "IDescriptionAnalyzer",
    "IDiffAnalyzer",
    "IPRScorer",
    "IGitHubClient",
    "IConfigLoader",
]


class ITitleAnalyzer(ABC):
    """Analyzes PR title quality."""

    @abstractmethod
    def analyze(self, title: str) -> list[tuple[str, bool, str]]:
        """Analyze a PR title.

        Args:
            title: The pull request title.

        Returns:
            A list of (check_name, passed, message) tuples.
        """


class IDescriptionAnalyzer(ABC):
    """Analyzes PR description quality."""

    @abstractmethod
    def analyze(self, body: str | None) -> list[tuple[str, bool, str]]:
        """Analyze a PR description body.

        Args:
            body: The pull request body/description text.

        Returns:
            A list of (check_name, passed, message) tuples.
        """


class IDiffAnalyzer(ABC):
    """Analyzes PR diff for size and quality signals."""

    @abstractmethod
    def analyze(self, diff: str, files: list[str]) -> list[tuple[str, bool, str]]:
        """Analyze a PR diff.

        Args:
            diff: The raw diff text.
            files: List of changed file paths.

        Returns:
            A list of (check_name, passed, message) tuples.
        """


class IPRScorer(ABC):
    """Aggregates check results into a final score."""

    @abstractmethod
    def score(self, checks: list[tuple[str, bool, str, int]]) -> int:
        """Calculate overall PR quality score.

        Args:
            checks: List of (name, passed, message, weight) tuples.

        Returns:
            An integer score from 0 to 100.
        """


class IGitHubClient(ABC):
    """Client for interacting with the GitHub API."""

    @abstractmethod
    async def get_pull_request(self, owner: str, repo: str, pr_number: int) -> dict[str, Any]:
        """Fetch pull request metadata.

        Args:
            owner: Repository owner.
            repo: Repository name.
            pr_number: Pull request number.

        Returns:
            A dict with PR metadata including title, body, and head SHA.
        """

    @abstractmethod
    async def get_pr_diff(self, owner: str, repo: str, pr_number: int) -> str:
        """Fetch the raw diff for a pull request.

        Args:
            owner: Repository owner.
            repo: Repository name.
            pr_number: Pull request number.

        Returns:
            The raw unified diff as a string.
        """

    @abstractmethod
    async def get_pr_files(self, owner: str, repo: str, pr_number: int) -> list[dict[str, Any]]:
        """Fetch the list of files changed in a pull request.

        Args:
            owner: Repository owner.
            repo: Repository name.
            pr_number: Pull request number.

        Returns:
            A list of file dicts with filename, additions, deletions.
        """

    @abstractmethod
    async def post_comment(self, owner: str, repo: str, pr_number: int, body: str) -> None:
        """Post a comment on a pull request.

        Args:
            owner: Repository owner.
            repo: Repository name.
            pr_number: Pull request number.
            body: Comment body in Markdown.
        """

    @abstractmethod
    async def create_check_run(
        self,
        owner: str,
        repo: str,
        head_sha: str,
        name: str,
        conclusion: str,
        title: str,
        summary: str,
    ) -> None:
        """Create a GitHub Check Run on a commit.

        Args:
            owner: Repository owner.
            repo: Repository name.
            head_sha: The commit SHA to attach the check to.
            name: Check run name.
            conclusion: One of success, failure, neutral.
            title: Check run output title.
            summary: Check run output summary in Markdown.
        """

    @abstractmethod
    async def request_changes(self, owner: str, repo: str, pr_number: int, body: str) -> None:
        """Submit a 'request changes' review on a pull request.

        Args:
            owner: Repository owner.
            repo: Repository name.
            pr_number: Pull request number.
            body: Review body in Markdown.
        """

    @abstractmethod
    async def get_file_content(self, owner: str, repo: str, path: str) -> str | None:
        """Retrieve a file from the repository.

        Args:
            owner: Repository owner.
            repo: Repository name.
            path: File path within the repository.

        Returns:
            The decoded file content, or None if the file does not exist.
        """


class IConfigLoader(ABC):
    """Loads per-repository configuration for PR Coach."""

    @abstractmethod
    async def load(self, owner: str, repo: str) -> Any:
        """Load configuration for a given repository.

        Args:
            owner: Repository owner.
            repo: Repository name.

        Returns:
            A configuration object.
        """
