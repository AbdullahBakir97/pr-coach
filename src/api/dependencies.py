"""FastAPI dependency injection helpers."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import Depends, Request

if TYPE_CHECKING:
    from src.application.orchestrator import AnalysisOrchestrator
    from src.application.webhook_handler import WebhookHandler
    from src.container import Container

__all__ = [
    "get_container",
    "get_orchestrator",
    "get_webhook_handler",
]


def get_container(request: Request) -> Container:
    """Retrieve the DI container stored on the application state.

    Args:
        request: The incoming FastAPI request.

    Returns:
        The application's Container instance.
    """
    return request.app.state.container


def get_webhook_handler(
    container: Container = Depends(get_container),
) -> WebhookHandler:
    """Provide the WebhookHandler from the container.

    Args:
        container: The DI container.

    Returns:
        The configured WebhookHandler.
    """
    return container.webhook_handler


def get_orchestrator(
    container: Container = Depends(get_container),
) -> AnalysisOrchestrator:
    """Provide the AnalysisOrchestrator from the container.

    Args:
        container: The DI container.

    Returns:
        The configured AnalysisOrchestrator.
    """
    return container.orchestrator
