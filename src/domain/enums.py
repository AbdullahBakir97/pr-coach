"""Enumerations for the PR Coach domain layer."""

from enum import StrEnum

__all__ = ["PRSize", "QualityLevel", "CheckConclusion"]


class PRSize(StrEnum):
    """Pull request size classification based on lines changed."""

    XS = "xs"  # < 10 lines
    SMALL = "small"  # 10-100 lines
    MEDIUM = "medium"  # 100-500 lines
    LARGE = "large"  # 500-1000 lines
    XL = "xl"  # > 1000 lines


class QualityLevel(StrEnum):
    """Quality tier derived from the PR quality score."""

    EXCELLENT = "excellent"  # 90-100
    GOOD = "good"  # 70-89
    FAIR = "fair"  # 50-69
    POOR = "poor"  # 30-49
    FAILING = "failing"  # 0-29


class CheckConclusion(StrEnum):
    """GitHub Check Run conclusion values."""

    SUCCESS = "success"
    FAILURE = "failure"
    NEUTRAL = "neutral"
