from typing import AsyncGenerator, List, Optional

from integrations.github.github.client import GitHubClient
from integrations.github.github.models.resources import (GitHubIssue,
                                                         GitHubPullRequest,
                                                         GitHubRepository,
                                                         GitHubUser,
                                                         GitHubWorkflow,
                                                         GitHubWorkflowRun)
from loguru import logger
from port_ocean.context.ocean import ocean


async def fetch_repositories(
    client: GitHubClient, organization: Optional[str] = None
) -> AsyncGenerator[List[GitHubRepository], None]:
    """Fetch repositories from GitHub."""
    logger.info(
        "Starting to fetch repositories from GitHub"
        + (f" for org: {organization}" if organization else "")
    )

    try:
        repo_count = 0
        async for repos_batch in client.get_repositories(org=organization):
            repo_count += len(repos_batch)
            logger.debug(
                f"Fetched {len(repos_batch)} repositories (total: {repo_count})"
            )
            yield repos_batch

    except Exception as e:
        logger.error(f"Error fetching repositories: {e}")
        if not ocean.integration_config.get("continue_on_error", False):
            raise


async def fetch_issues(
    client: GitHubClient, repositories: List[GitHubRepository], state: str = "all"
) -> AsyncGenerator[List[GitHubIssue], None]:
    """Fetch issues from repositories."""
    logger.info(f"Starting to fetch issues from {len(repositories)} repositories")

    for repo in repositories:
        try:
            issue_count = 0
            async for issues_batch in client.get_repository_issues(
                repo.owner.login, repo.name, state=state
            ):
                issue_count += len(issues_batch)
                logger.debug(
                    f"Fetched {len(issues_batch)} issues from {repo.full_name} (total: {issue_count})"
                )
                # Add repository context to issues
                for issue in issues_batch:
                    issue.repository = repo
                yield issues_batch

        except Exception as e:
            logger.error(f"Error fetching issues for {repo.full_name}: {e}")
            if not ocean.integration_config.get("continue_on_error", False):
                raise


async def fetch_pull_requests(
    client: GitHubClient, repositories: List[GitHubRepository], state: str = "all"
) -> AsyncGenerator[List[GitHubPullRequest], None]:
    """Fetch pull requests from repositories."""
    logger.info(
        f"Starting to fetch pull requests from {len(repositories)} repositories"
    )

    for repo in repositories:
        try:
            pr_count = 0
            async for prs_batch in client.get_repository_pull_requests(
                repo.owner.login, repo.name, state=state
            ):
                pr_count += len(prs_batch)
                logger.debug(
                    f"Fetched {len(prs_batch)} pull requests from {repo.full_name} (total: {pr_count})"
                )
                # Add repository context to PRs
                for pr in prs_batch:
                    pr.repository = repo
                yield prs_batch

        except Exception as e:
            logger.error(f"Error fetching pull requests for {repo.full_name}: {e}")
            if not ocean.integration_config.get("continue_on_error", False):
                raise


async def fetch_workflows(
    client: GitHubClient, repositories: List[GitHubRepository]
) -> AsyncGenerator[List[GitHubWorkflow], None]:
    """Fetch workflows from repositories."""
    logger.info(f"Starting to fetch workflows from {len(repositories)} repositories")

    for repo in repositories:
        try:
            async for workflows_batch in client.get_repository_workflows(
                repo.owner.login, repo.name
            ):
                logger.debug(
                    f"Fetched {len(workflows_batch)} workflows from {repo.full_name}"
                )
                # Add repository context to workflows
                for workflow in workflows_batch:
                    workflow.repository = repo
                yield workflows_batch

        except Exception as e:
            logger.error(f"Error fetching workflows for {repo.full_name}: {e}")
            if not ocean.integration_config.get("continue_on_error", False):
                raise


async def fetch_workflow_runs(
    client: GitHubClient, repositories: List[GitHubRepository]
) -> AsyncGenerator[List[GitHubWorkflowRun], None]:
    """Fetch workflow runs from repositories."""
    logger.info(
        f"Starting to fetch workflow runs from {len(repositories)} repositories"
    )

    for repo in repositories:
        try:
            run_count = 0
            async for runs_batch in client.get_workflow_runs(
                repo.owner.login, repo.name
            ):
                run_count += len(runs_batch)
                logger.debug(
                    f"Fetched {len(runs_batch)} workflow runs from {repo.full_name} (total: {run_count})"
                )
                yield runs_batch

        except Exception as e:
            logger.error(f"Error fetching workflow runs for {repo.full_name}: {e}")
            if not ocean.integration_config.get("continue_on_error", False):
                raise


async def fetch_organization_members(
    client: GitHubClient, organization: str
) -> AsyncGenerator[List[GitHubUser], None]:
    """Fetch organization members."""
    logger.info(f"Starting to fetch members from organization: {organization}")

    try:
        member_count = 0
        async for members_batch in client.get_organization_members(organization):
            member_count += len(members_batch)
            logger.debug(
                f"Fetched {len(members_batch)} members (total: {member_count})"
            )
            yield members_batch

    except Exception as e:
        logger.error(f"Error fetching organization members: {e}")
        if not ocean.integration_config.get("continue_on_error", False):
            raise
