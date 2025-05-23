from typing import Any, List

from integrations.github.github.client import GitHubClient
from integrations.github.github.core import (fetch_issues,
                                             fetch_organization_members,
                                             fetch_pull_requests,
                                             fetch_repositories,
                                             fetch_workflow_runs,
                                             fetch_workflows)
from integrations.github.github.models.resources import GitHubRepository
from loguru import logger
from port_ocean.context.ocean import ocean
from port_ocean.core.integrations.base import BaseIntegration
from port_ocean.core.ocean_types import ASYNC_GENERATOR_RESYNC_TYPE


class GitHubIntegration(BaseIntegration):
    class AppConfigHandlerSettings:
        base_path = "github"

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        self.token = config.get("token", "")
        self.organization = config.get("organization")
        self.base_url = config.get("base_url", "https://api.github.com")

        if not self.token:
            raise ValueError("GitHub token is required")

    async def _get_client(self) -> GitHubClient:
        """Get configured GitHub client."""
        return GitHubClient(self.token, self.base_url)

    async def _get_repositories(self) -> List[GitHubRepository]:
        """Get all repositories for the configured organization or user."""
        repositories = []
        async with await self._get_client() as client:
            async for repos_batch in fetch_repositories(client, self.organization):
                repositories.extend(repos_batch)
        return repositories

    @ocean.on_resync("repository")
    async def on_resync_repositories(self, kind: str) -> ASYNC_GENERATOR_RESYNC_TYPE:
        """Resync repositories from GitHub."""
        logger.info(f"Resyncing repositories for kind: {kind}")

        async with await self._get_client() as client:
            async for repos_batch in fetch_repositories(client, self.organization):
                for repo in repos_batch:
                    yield [repo.dict(), repo.id]

    @ocean.on_resync("issue")
    async def on_resync_issues(self, kind: str) -> ASYNC_GENERATOR_RESYNC_TYPE:
        """Resync issues from GitHub repositories."""
        logger.info(f"Resyncing issues for kind: {kind}")

        repositories = await self._get_repositories()

        async with await self._get_client() as client:
            async for issues_batch in fetch_issues(client, repositories):
                for issue in issues_batch:
                    # Create composite ID with repo context
                    issue_id = f"{issue.repository.full_name}#{issue.number}"
                    yield [issue.dict(), issue_id]

    @ocean.on_resync("pullRequest")
    async def on_resync_pull_requests(self, kind: str) -> ASYNC_GENERATOR_RESYNC_TYPE:
        """Resync pull requests from GitHub repositories."""
        logger.info(f"Resyncing pull requests for kind: {kind}")

        repositories = await self._get_repositories()

        async with await self._get_client() as client:
            async for prs_batch in fetch_pull_requests(client, repositories):
                for pr in prs_batch:
                    # Create composite ID with repo context
                    pr_id = f"{pr.repository.full_name}#{pr.number}"
                    yield [pr.dict(), pr_id]

    @ocean.on_resync("workflow")
    async def on_resync_workflows(self, kind: str) -> ASYNC_GENERATOR_RESYNC_TYPE:
        """Resync workflows from GitHub repositories."""
        logger.info(f"Resyncing workflows for kind: {kind}")

        repositories = await self._get_repositories()

        async with await self._get_client() as client:
            async for workflows_batch in fetch_workflows(client, repositories):
                for workflow in workflows_batch:
                    # Create composite ID with repo context
                    workflow_id = f"{workflow.repository.full_name}/{workflow.id}"
                    yield [workflow.dict(), workflow_id]

    @ocean.on_resync("workflowRun")
    async def on_resync_workflow_runs(self, kind: str) -> ASYNC_GENERATOR_RESYNC_TYPE:
        """Resync workflow runs from GitHub repositories."""
        logger.info(f"Resyncing workflow runs for kind: {kind}")

        repositories = await self._get_repositories()

        async with await self._get_client() as client:
            async for runs_batch in fetch_workflow_runs(client, repositories):
                for run in runs_batch:
                    yield [run.dict(), run.id]

    @ocean.on_resync("user")
    async def on_resync_users(self, kind: str) -> ASYNC_GENERATOR_RESYNC_TYPE:
        """Resync organization members from GitHub."""
        logger.info(f"Resyncing users for kind: {kind}")

        if not self.organization:
            logger.warning("No organization configured, skipping user sync")
            return

        async with await self._get_client() as client:
            async for members_batch in fetch_organization_members(
                client, self.organization
            ):
                for member in members_batch:
                    yield [member.dict(), member.id]
