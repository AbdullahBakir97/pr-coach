"""Load per-repository configuration from .github/pr-coach.yml."""

from __future__ import annotations

import logging

import yaml
from pydantic import ValidationError

from src.infrastructure.github.client import GitHubClient

from .schema import PRCoachConfig

__all__ = ["ConfigLoader"]

logger = logging.getLogger(__name__)

_CONFIG_PATH = ".github/pr-coach.yml"


class ConfigLoader:
    """Loads and validates per-repo PR Coach configuration via the GitHub API.

    Falls back to sensible defaults when the file is missing or contains
    invalid YAML.
    """

    def __init__(self, github_client: GitHubClient) -> None:
        self._client = github_client

    async def load(self, owner: str, repo: str) -> PRCoachConfig:
        """Load configuration for *owner/repo*.

        Args:
            owner: Repository owner.
            repo: Repository name.

        Returns:
            A validated PRCoachConfig instance.
        """
        content = await self._client.get_file_content(owner, repo, _CONFIG_PATH)

        if content is None:
            logger.debug("No config file found for %s/%s -- using defaults", owner, repo)
            return PRCoachConfig()

        try:
            data = yaml.safe_load(content)
            if not isinstance(data, dict):
                logger.warning("Config for %s/%s is not a mapping -- using defaults", owner, repo)
                return PRCoachConfig()
            return PRCoachConfig(**data)
        except yaml.YAMLError as exc:
            logger.warning("Invalid YAML in config for %s/%s: %s -- using defaults", owner, repo, exc)
            return PRCoachConfig()
        except ValidationError as exc:
            logger.warning("Invalid config for %s/%s: %s -- using defaults", owner, repo, exc)
            return PRCoachConfig()
