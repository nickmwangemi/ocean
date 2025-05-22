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

    async def fetch_with_retry(self, endpoint, max_retries=3, params=None):
        """Fetch data from GitHub API with retry logic and pagination support."""
        session = None
        try:
            session = aiohttp.ClientSession()
            all_results = []
            next_url = f"{self.base_url}{endpoint}"

            while next_url:
                for attempt in range(max_retries):
                    try:
                        async with session.get(next_url, headers=self.headers, params=params) as response:
                            response_text = await response.text()

                            # Handle rate limiting
                            if response.status == 403 and "rate limit" in response_text:
                                retry_after = int(response.headers.get("Retry-After", 10))
                                logger.info(f"Rate limit exceeded. Retrying after {retry_after} seconds.")
                                await asyncio.sleep(retry_after)
                                break

                            # Handle other status codes
                            if response.status >= 400:
                                if response.status == 404:
                                    logger.warning(f"Resource not found: {next_url}")
                                    return []
                                response.raise_for_status()

                            # Process response
                            results = await response.json()

                            # Handle both array and single object responses
                            if isinstance(results, list):
                                all_results.extend(results)
                            else:
                                return results  # If it's not a list, return directly

                            # Handle pagination
                            if 'Link' in response.headers:
                                links = self._parse_link_header(response.headers['Link'])
                                next_url = links.get('next')
                            else:
                                next_url = None

                            break  # Success, exit retry loop

                    except aiohttp.ClientError as e:
                        if attempt == max_retries - 1:
                            logger.error(f"Failed to fetch data from {next_url}: {e}")
                            raise
                        backoff_time = 2 ** attempt
                        logger.info(f"Retrying in {backoff_time} seconds...")
                        await asyncio.sleep(backoff_time)

            return all_results
        finally:
            if session and not session.closed:
                await session.close()

    def _parse_link_header(self, link_header):
        """Parse GitHub API Link header for pagination."""
        links = {}
        if not link_header:
            return links

        for link in link_header.split(','):
            parts = link.split(';')
            url = parts[0].strip('<> ')
            rel = parts[1].split('=')[1].strip('"')
            links[rel] = url

        return links
