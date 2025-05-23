import asyncio
from typing import Any, AsyncGenerator, Dict, List, Optional
from urllib.parse import parse_qs, urljoin, urlparse

import aiohttp
from integrations.github.github.models.resources import (GitHubIssue,
                                                         GitHubPullRequest,
                                                         GitHubRepository,
                                                         GitHubUser,
                                                         GitHubWorkflow,
                                                         GitHubWorkflowRun)
from loguru import logger


class GitHubClient:
    def __init__(self, token: str, base_url: str = "https://api.github.com"):
        self.token = token
        self.base_url = base_url.rstrip("/")
        self._session: Optional[aiohttp.ClientSession] = None

        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "Port-Ocean-GitHub-Integration",
        }

    async def __aenter__(self):
        self._session = aiohttp.ClientSession(
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=30),
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()

    @property
    def session(self) -> aiohttp.ClientSession:
        if not self._session:
            raise RuntimeError(
                "Client session not initialized. Use async context manager."
            )
        return self._session

    async def _make_request(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        full_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Make authenticated request to GitHub API."""
        url = full_url or urljoin(f"{self.base_url}/", endpoint)

        try:
            async with self.session.request(method, url, params=params) as response:
                # Handle rate limiting
                if response.status == 403:
                    reset_time = response.headers.get("X-RateLimit-Reset")
                    remaining = response.headers.get("X-RateLimit-Remaining", "0")

                    if remaining == "0" and reset_time:
                        wait_time = int(reset_time) - int(
                            asyncio.get_event_loop().time()
                        )
                        if wait_time > 0:
                            logger.warning(
                                f"Rate limit exceeded. Waiting {wait_time} seconds"
                            )
                            await asyncio.sleep(wait_time)
                            return await self._make_request(
                                endpoint, method, params, full_url
                            )

                if response.status == 422:  # Validation failed
                    error_data = await response.json()
                    logger.error(f"GitHub API validation error: {error_data}")
                    raise aiohttp.ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=response.status,
                        message=str(error_data),
                    )

                response.raise_for_status()
                return await response.json()

        except aiohttp.ClientError as e:
            logger.error(f"Request failed for {endpoint}: {e}")
            raise

    async def _paginated_request(
        self,
        endpoint: str,
        per_page: int = 100,
        params: Optional[Dict[str, Any]] = None,
    ) -> AsyncGenerator[List[Dict[str, Any]], None]:
        """Handle paginated requests using GitHub's Link header."""
        url = urljoin(f"{self.base_url}/", endpoint)
        request_params = {"per_page": per_page}
        if params:
            request_params |= params

        while url:
            try:
                async with self.session.get(
                    url,
                    params=(
                        request_params
                        if url == urljoin(f"{self.base_url}/", endpoint)
                        else None
                    ),
                ) as response:
                    # Handle rate limiting
                    if response.status == 403:
                        reset_time = response.headers.get("X-RateLimit-Reset")
                        remaining = response.headers.get("X-RateLimit-Remaining", "0")

                        if remaining == "0" and reset_time:
                            wait_time = int(reset_time) - int(
                                asyncio.get_event_loop().time()
                            )
                            if wait_time > 0:
                                logger.warning(
                                    f"Rate limit exceeded. Waiting {wait_time} seconds"
                                )
                                await asyncio.sleep(wait_time)
                                continue

                    response.raise_for_status()
                    data = await response.json()

                    if not data:
                        break

                    yield data

                    # Parse Link header for next page
                    link_header = response.headers.get("Link")
                    url = None

                    if link_header:
                        links = {}
                        for link in link_header.split(","):
                            link_url, rel = link.strip().split(";")
                            link_url = link_url.strip("<>")
                            rel = rel.strip().split("=")[1].strip('"')
                            links[rel] = link_url

                        url = links.get("next")

                    request_params = None  # Don't send params for subsequent requests

            except Exception as e:
                logger.error(f"Error in paginated request for {endpoint}: {e}")
                break

    async def get_repositories(
        self, org: Optional[str] = None
    ) -> AsyncGenerator[List[GitHubRepository], None]:
        """Fetch repositories for organization or authenticated user."""
        endpoint = f"orgs/{org}/repos" if org else "user/repos"
        async for page_data in self._paginated_request(
            endpoint, params={"sort": "updated"}
        ):
            yield [GitHubRepository(**item) for item in page_data]

    async def get_repository_issues(
        self, owner: str, repo: str, state: str = "all"
    ) -> AsyncGenerator[List[GitHubIssue], None]:
        """Fetch issues for a specific repository."""
        endpoint = f"repos/{owner}/{repo}/issues"
        params = {"state": state, "sort": "updated"}

        async for page_data in self._paginated_request(endpoint, params=params):
            if issues := [
                GitHubIssue(**item) for item in page_data if "pull_request" not in item
            ]:
                yield issues

    async def get_repository_pull_requests(
        self, owner: str, repo: str, state: str = "all"
    ) -> AsyncGenerator[List[GitHubPullRequest], None]:
        """Fetch pull requests for a specific repository."""
        endpoint = f"repos/{owner}/{repo}/pulls"
        params = {"state": state, "sort": "updated"}

        async for page_data in self._paginated_request(endpoint, params=params):
            yield [GitHubPullRequest(**item) for item in page_data]

    async def get_repository_workflows(
        self, owner: str, repo: str
    ) -> AsyncGenerator[List[GitHubWorkflow], None]:
        """Fetch workflows for a specific repository."""
        endpoint = f"repos/{owner}/{repo}/actions/workflows"

        try:
            data = await self._make_request(endpoint)
            if workflows := [
                GitHubWorkflow(**item) for item in data.get("workflows", [])
            ]:
                yield workflows
        except Exception as e:
            logger.error(f"Error fetching workflows for {owner}/{repo}: {e}")

    async def get_workflow_runs(
        self, owner: str, repo: str, workflow_id: Optional[int] = None
    ) -> AsyncGenerator[List[GitHubWorkflowRun], None]:
        """Fetch workflow runs for a repository or specific workflow."""
        if workflow_id:
            endpoint = f"repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs"
        else:
            endpoint = f"repos/{owner}/{repo}/actions/runs"

        async for page_data in self._paginated_request(endpoint):
            if workflow_runs := [
                GitHubWorkflowRun(**item) for item in page_data.get("workflow_runs", [])
            ]:
                yield workflow_runs

    async def get_organization_members(
        self, org: str
    ) -> AsyncGenerator[List[GitHubUser], None]:
        """Fetch members of an organization."""
        endpoint = f"orgs/{org}/members"

        async for page_data in self._paginated_request(endpoint):
            yield [GitHubUser(**item) for item in page_data]

    async def get_user(self, username: str) -> Optional[GitHubUser]:
        """Fetch a specific user."""
        try:
            data = await self._make_request(f"users/{username}")
            return GitHubUser(**data)
        except Exception as e:
            logger.error(f"Error fetching user {username}: {e}")
            return None
