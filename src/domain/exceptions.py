"""Custom exceptions for PR Coach."""

__all__ = [
    "PRCoachError",
    "AnalysisError",
    "GitHubAPIError",
    "ConfigurationError",
]


class PRCoachError(Exception):
    """Base exception for all PR Coach errors."""


class AnalysisError(PRCoachError):
    """Raised when PR analysis fails."""


class GitHubAPIError(PRCoachError):
    """Raised when a GitHub API call fails."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class ConfigurationError(PRCoachError):
    """Raised when configuration is invalid or missing."""
