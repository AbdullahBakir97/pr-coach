"""Orchestrates the full PR analysis workflow."""

from __future__ import annotations

import logging

from src.analyzers.description_analyzer import DescriptionAnalyzer
from src.analyzers.diff_analyzer import DiffAnalyzer
from src.analyzers.pr_scorer import PRScorer
from src.analyzers.title_analyzer import TitleAnalyzer
from src.domain.entities import PRAnalysis
from src.domain.enums import PRSize
from src.generators.check_builder import CheckBuilder
from src.generators.comment_builder import CommentBuilder
from src.infrastructure.config.loader import ConfigLoader
from src.infrastructure.github.client import GitHubClient

__all__ = ["AnalysisOrchestrator"]

logger = logging.getLogger(__name__)


class AnalysisOrchestrator:
    """Coordinates PR analysis: fetching data, running checks, and reporting.

    Ties together the GitHub client, analyzers, generators, and
    configuration loader into a single high-level workflow.
    """

    def __init__(
        self,
        github_client: GitHubClient,
        title_analyzer: TitleAnalyzer,
        description_analyzer: DescriptionAnalyzer,
        diff_analyzer: DiffAnalyzer,
        pr_scorer: PRScorer,
        comment_builder: CommentBuilder,
        check_builder: CheckBuilder,
        config_loader: ConfigLoader,
    ) -> None:
        self._client = github_client
        self._title_analyzer = title_analyzer
        self._description_analyzer = description_analyzer
        self._diff_analyzer = diff_analyzer
        self._pr_scorer = pr_scorer
        self._comment_builder = comment_builder
        self._check_builder = check_builder
        self._config_loader = config_loader

    async def analyze_pr(
        self,
        owner: str,
        repo: str,
        pr_number: int,
        head_sha: str,
        installation_id: int,
    ) -> PRAnalysis:
        """Run the full PR analysis workflow.

        Steps:
            1. Set installation ID on the client.
            2. Load per-repo configuration.
            3. Fetch PR metadata, diff, and files.
            4. Run all analyzers.
            5. Score the results.
            6. Create a GitHub Check Run.
            7. Post a coaching comment.
            8. Request changes if configured and score is low.

        Args:
            owner: Repository owner.
            repo: Repository name.
            pr_number: Pull-request number.
            head_sha: HEAD commit SHA.
            installation_id: GitHub App installation ID.

        Returns:
            The PRAnalysis result.
        """
        self._client.set_installation_id(installation_id)

        config = await self._config_loader.load(owner, repo)

        if not config.enabled:
            logger.info("PR Coach is disabled for %s/%s", owner, repo)
            return self._empty_result(pr_number)

        # Update analyzer settings from config
        self._diff_analyzer = DiffAnalyzer(
            max_files=config.max_files,
            max_lines=config.max_lines,
        )
        self._pr_scorer = PRScorer(min_score=config.min_score)

        # Fetch PR data
        pr_data = await self._client.get_pull_request(owner, repo, pr_number)
        title = pr_data.get("title", "")
        body = pr_data.get("body")
        diff = await self._client.get_pr_diff(owner, repo, pr_number)
        files = await self._client.get_pr_files(owner, repo, pr_number)

        # Run analyzers
        changed_filenames = [f.get("filename", "") for f in files]
        all_checks: list[tuple[str, bool, str]] = []
        all_checks.extend(self._title_analyzer.analyze(title))
        all_checks.extend(self._description_analyzer.analyze(body, changed_filenames))
        all_checks.extend(self._diff_analyzer.analyze(diff, files))

        # Score
        score, checks = self._pr_scorer.score(all_checks)
        quality_level = self._pr_scorer.determine_quality_level(score)
        conclusion = self._pr_scorer.determine_conclusion(score)

        # Calculate size info
        total_additions = sum(int(f.get("additions", 0)) for f in files)
        total_deletions = sum(int(f.get("deletions", 0)) for f in files)
        total_lines = total_additions + total_deletions
        pr_size = DiffAnalyzer._classify_size(total_lines)

        # Build result
        result = PRAnalysis(
            pr_number=pr_number,
            title=title,
            score=score,
            quality_level=quality_level,
            pr_size=pr_size,
            conclusion=conclusion,
            checks=checks,
            suggestions=[],
            lines_added=total_additions,
            lines_removed=total_deletions,
            files_changed=len(files),
        )

        # Create check run
        check_title = self._check_builder.build_title(result)
        summary = self._check_builder.build_summary(result)
        check_conclusion = self._check_builder.build_conclusion(result)

        await self._client.create_check_run(
            owner=owner,
            repo=repo,
            head_sha=head_sha,
            name="PR Coach",
            title=check_title,
            summary=summary,
            conclusion=check_conclusion,
        )

        # Post comment if action requires it
        if config.action in ("comment", "request-changes", "block"):
            comment = self._comment_builder.build(result)
            await self._client.post_comment(owner, repo, pr_number, comment)

        # Request changes if action requires it and the check failed
        if config.action in ("request-changes", "block") and not result.passed:
            comment = self._comment_builder.build(result)
            await self._client.request_changes(owner, repo, pr_number, comment)

        logger.info(
            "Analysis complete for %s/%s#%d: score=%d conclusion=%s",
            owner,
            repo,
            pr_number,
            result.score,
            check_conclusion,
        )

        return result

    @staticmethod
    def _empty_result(pr_number: int) -> PRAnalysis:
        """Create an empty result for skipped PRs.

        Args:
            pr_number: The pull-request number.

        Returns:
            A minimal PRAnalysis.
        """
        from src.domain.enums import CheckConclusion, QualityLevel

        return PRAnalysis(
            pr_number=pr_number,
            title="",
            score=0,
            quality_level=QualityLevel.FAILING,
            pr_size=PRSize.XS,
            conclusion=CheckConclusion.NEUTRAL,
            checks=[],
            suggestions=[],
        )
