"""Configuration infrastructure for PR Coach."""

from .loader import ConfigLoader
from .schema import PRCoachConfig

__all__ = ["PRCoachConfig", "ConfigLoader"]
