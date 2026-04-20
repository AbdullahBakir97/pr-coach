"""Pydantic request and response models for the API layer."""

from __future__ import annotations

from pydantic import BaseModel, Field

__all__ = [
    "AnalyzeRequest",
    "AnalyzeResponse",
    "CheckResultResponse",
    "HealthResponse",
    "WebhookResponse",
]


class AnalyzeRequest(BaseModel):
    """Request body for the ``/api/v1/analyze`` endpoint."""

    title: str = Field(..., min_length=1, description="PR title to analyse")
    description: str = Field(default="", description="PR description/body text")


class CheckResultResponse(BaseModel):
    """A single check result in the analysis response."""

    name: str
    passed: bool
    message: str


class AnalyzeResponse(BaseModel):
    """Response body for the ``/api/v1/analyze`` endpoint."""

    score: int
    quality_level: str
    checks: list[CheckResultResponse] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)


class HealthResponse(BaseModel):
    """Response body for the ``/health`` endpoint."""

    status: str = "ok"
    uptime: float = 0.0
    version: str = "1.0.0"


class WebhookResponse(BaseModel):
    """Response body for the ``/webhook`` endpoint."""

    received: bool = True
