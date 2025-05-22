import asyncio
import logging

import aiohttp

logger = logging.getLogger(__name__)


class GitHubClient:
    def __init__(self, api_token, base_url):
        self.api_token = api_token
        self.base_url = base_url
        self.headers = {
            "Authorization": f"token {self.api_token}",
            "Accept": "application/vnd.github.v3+json",
        }

    async def fetch_with_retry(self, endpoint, max_retries=3):
        for attempt in range(max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{self.base_url}{endpoint}", headers=self.headers
                    ) as response:
                        if (
                            response.status == 403
                            and "rate limit" in await response.text()
                        ):
                            retry_after = int(response.headers.get("Retry-After", 10))
                            logger.info(
                                f"Rate limit exceeded. Retrying after {retry_after} seconds."
                            )
                            await asyncio.sleep(retry_after)
                            continue
                        response.raise_for_status()
                        return await response.json()
            except aiohttp.ClientError as e:
                if attempt == max_retries - 1:
                    logger.error(f"Failed to fetch data from {endpoint}: {e}")
                    raise e
                logger.info(f"Retrying in {2 ** attempt} seconds...")
                await asyncio.sleep(2**attempt)
