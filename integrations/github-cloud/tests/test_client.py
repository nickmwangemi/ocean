from unittest.mock import AsyncMock

import pytest


@pytest.mark.asyncio
async def test_fetch_with_retry():
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = [{"id": 1, "name": "repo1"}]
    mock_response.text.return_value = ""

    mock_session = AsyncMock()
    mock_session.get.return_value.__aenter__.return_value = mock_response

    mock_client = GitHubClient(
        api_token="test_token", base_url="https://api.github.com"
    )
    mock_client.client_session = mock_session

    data = await mock_client.fetch_with_retry("/repos/test_org/repo1")
    assert data == [{"id": 1, "name": "repo1"}]
