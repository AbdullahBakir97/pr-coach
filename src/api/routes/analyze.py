"""Public analysis endpoint for the dashboard demo."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends

from src.api.dependencies import get_container
from src.api.schemas import AnalyzeRequest, AnalyzeResponse, CheckResultResponse
from src.container import Container

__all__ = ["router"]

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["analyze"])


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_pr_description(
    request: AnalyzeRequest,
    container: Container = Depends(get_container),
) -> AnalyzeResponse:
    """Run PR analysis on arbitrary title and description text.

    This endpoint is intended for the interactive dashboard demo and
    does not require GitHub authentication.

    Args:
        request: The analysis request containing a title and description.
        container: The DI container (injected).

    Returns:
        An AnalyzeResponse with score, quality level, checks, and suggestions.
    """
    title = request.title
    description = request.description

    # Run analyzers
    all_checks: list[tuple[str, bool, str]] = []
    all_checks.extend(container.title_analyzer.analyze(title))
    all_checks.extend(container.description_analyzer.analyze(description or None))

    # Score
    score, checks = container.pr_scorer.score(all_checks)
    quality_level = container.pr_scorer.determine_quality_level(score)

    # Build suggestions from failed checks
    suggestions = [c.message for c in checks if not c.passed]

    return AnalyzeResponse(
        score=score,
        quality_level=quality_level.value,
        checks=[CheckResultResponse(name=c.name, passed=c.passed, message=c.message) for c in checks],
        suggestions=suggestions,
    )
