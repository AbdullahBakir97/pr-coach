"""Pydantic models for per-repository configuration (.github/pr-coach.yml)."""

from __future__ import annotations

from pydantic import BaseModel, Field

__all__ = ["PRCoachConfig"]


class PRCoachConfig(BaseModel):
    """Per-repository configuration for PR Coach.

    Loaded from ``.github/pr-coach.yml`` in the target repository.
    All fields have sensible defaults so the config file is optional.
    """

    enabled: bool = True
    min_score: int = Field(default=60, ge=0, le=100)
    require_linked_issue: bool = Field(default=False, description="Fail if no linked issue")
    require_description: bool = Field(default=True, description="Fail if description is empty")
    require_tests: bool = Field(default=False, description="Fail if no test files included")
    max_files: int = Field(default=20, ge=1, description="Maximum files before warning")
    max_lines: int = Field(default=500, ge=1, description="Maximum lines before warning")
    action: str = Field(default="check", description="check | comment | request-changes | block")
