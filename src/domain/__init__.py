"""Domain layer for PR Coach."""

from .entities import PRAnalysis
from .enums import CheckConclusion, PRSize, QualityLevel
from .exceptions import AnalysisError, ConfigurationError, GitHubAPIError, PRCoachError

__all__ = [
    "PRAnalysis",
    "PRSize",
    "QualityLevel",
    "CheckConclusion",
    "PRCoachError",
    "AnalysisError",
    "GitHubAPIError",
    "ConfigurationError",
]
