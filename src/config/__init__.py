"""Application configuration for PR Coach."""

from .logging import configure_logging
from .settings import Settings

__all__ = ["Settings", "configure_logging"]
