import logging
import os

from port_ocean.context.ocean import ocean

import github_integration.config
from github_integration.client import GitHubClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for client and config
client = None

@ocean.on_start()
async def on_start():
    """Initialize the GitHub client when the integration starts"""
    global client

    # Load GitHub integration configuration
    config = github_integration.config.load_github_integration_config()

    # Initialize GitHub client
    client = GitHubClient(
        api_token=config.api_token,
        base_url=config.base_url,
    )

    logger.info("✅ GitHub integration initialized.")

async def fetch_repositories(org: str):
    """Fetch repositories for an organization"""
    data = await client.fetch_with_retry(f"/orgs/{org}/repos")
    for repo in data:
        yield repo

async def fetch_pull_requests(org: str, repo: str):
    """Fetch pull requests for a repository"""
    data = await client.fetch_with_retry(f"/repos/{org}/{repo}/pulls")
    for pr in data:
        yield pr

async def fetch_issues(org: str, repo: str):
    """Fetch issues for a repository"""
    data = await client.fetch_with_retry(f"/repos/{org}/{repo}/issues")
    for issue in data:
        yield issue

async def fetch_teams(org: str):
    """Fetch teams for an organization"""
    data = await client.fetch_with_retry(f"/orgs/{org}/teams")
    for team in data:
        yield team

async def fetch_workflows(org: str, repo: str):
    """Fetch workflows for a repository"""
    data = await client.fetch_with_retry(f"/repos/{org}/{repo}/actions/workflows")
    workflows = data.get("workflows", []) if isinstance(data, dict) else data
    for workflow in workflows:
        yield workflow

@ocean.on_resync()
async def on_resync(kind: str):
    """Handle resync events for different resource types"""
    logger.info(f"Starting resync for kind: {kind}")

    if not client:
        logger.error("GitHub client not initialized")
        return []

    try:
        # Get configuration - you should configure these properly
        org = os.getenv("GITHUB_ORG")
        repo = os.getenv("GITHUB_REPO")
        if not org or not repo:
            logger.error(
                "Missing required environment variables: GITHUB_ORG and/or GITHUB_REPO"
            )
            return []

        match kind:
            case "repository":
                repositories = []
                async for repo_data in fetch_repositories(org):
                    repositories.append(repo_data)
                logger.info(f"Fetched {len(repositories)} repositories")
                return repositories

            case "pull_request":
                pull_requests = []
                async for pr in fetch_pull_requests(org, repo):
                    pull_requests.append(pr)
                logger.info(f"Fetched {len(pull_requests)} pull requests")
                return pull_requests

            case "issue":
                issues = []
                async for issue in fetch_issues(org, repo):
                    issues.append(issue)
                logger.info(f"Fetched {len(issues)} issues")
                return issues

            case "team":
                teams = []
                async for team in fetch_teams(org):
                    teams.append(team)
                logger.info(f"Fetched {len(teams)} teams")
                return teams

            case "workflow":
                workflows = []
                async for workflow in fetch_workflows(org, repo):
                    workflows.append(workflow)
                logger.info(f"Fetched {len(workflows)} workflows")
                return workflows

            case _:
                logger.warning(f"Unknown kind: {kind}")
                return []

    except Exception as e:
        logger.error(f"Error during resync for kind {kind}: {e}")
        return []

if __name__ == "__main__":
    ocean.run()
